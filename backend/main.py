from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from httpx import AsyncClient, ConnectTimeout, ConnectError
from duckduckgo_search import DDGS
import json
from typing import List, Optional
import asyncio
import random
from datetime import datetime, timedelta

app = FastAPI(title="Perspicuity API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str
    context_results: Optional[int] = 3


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str


last_search_time = datetime.min


async def search_web(query: str, num_results: Optional[int] = 3) -> List[dict]:
    global last_search_time
    results: List[dict] = []

    # Ensure at least 3 seconds between searches to respect rate limits
    time_since_last = datetime.now() - last_search_time
    if time_since_last < timedelta(seconds=3):
        await asyncio.sleep(3 - time_since_last.total_seconds())

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            # Add small random delay to avoid precise patterns
            await asyncio.sleep(random.uniform(0.5, 1.5))

            with DDGS() as ddgs:
                # Using the newer API
                for r in ddgs.text(query, max_results=num_results or 3):
                    try:
                        results.append(
                            {
                                "title": r.get("title", "No title"),
                                "link": r.get("link", ""),
                                "snippet": r.get("snippet", "No description available"),
                            }
                        )
                    except (KeyError, AttributeError) as e:
                        print(f"Error processing search result: {e}")
                        continue

                    if len(results) >= (num_results or 3):
                        break

                last_search_time = datetime.now()
                if results:  # If we got any results, return them
                    return results
                raise Exception("No results found")

        except Exception as e:
            print(f"Search error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt) + random.uniform(0, 1)
                print(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
            else:
                print("All search attempts failed, proceeding without search results")

    return results  # Return empty list if all retries failed


async def get_llm_response(query: str, context: List[dict]) -> str:
    async with AsyncClient() as client:
        try:
            # First check if the model is available
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=503,
                    detail="Ollama service is not available. Please ensure Ollama is running.",
                )

            models = response.json().get("models", [])
            if not any(model.get("name") == "deepseek-r1:14b" for model in models):
                raise HTTPException(
                    status_code=404,
                    detail="DeepSeek 14B model is not available. Please run 'ollama pull deepseek-r1:14b' first.",
                )

            # Prepare the prompt
            prompt = f"""Answer the following question. Include citations if you have any search results to reference.

User Question: {query}

"""
            if context:
                formatted_context = "\n\n".join(
                    [
                        f"Source: {item['link']}\nTitle: {item['title']}\n{item['snippet']}"
                        for item in context
                    ]
                )
                prompt = f"""Based on the following search results, answer the user's question. 
If the search results don't contain relevant information, say so and answer based on your knowledge.
Include relevant source links in your response.

Search Results:
{formatted_context}

User Question: {query}

Answer: """

            # Make request to generate response
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "deepseek-r1:14b", "prompt": prompt, "stream": False},
                timeout=30.0,  # Add timeout
            )

            if response.status_code != 200:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json().get("error", "Unknown error")
                except:
                    pass
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LLM request failed: {error_detail}",
                )

            response_data = response.json()
            if "error" in response_data:
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM generation error: {response_data['error']}",
                )

            return response_data["response"]

        except ConnectTimeout:
            raise HTTPException(
                status_code=504, detail="LLM request timed out. Please try again."
            )
        except ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama. Please ensure the service is running.",
            )
        except Exception as e:
            print(f"Unexpected error in LLM response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@app.post("/api/query")
async def process_query(query: Query):
    try:
        # Get search results (now with retry logic)
        search_results = await search_web(query.text, query.context_results)

        # Get LLM response
        answer = await get_llm_response(query.text, search_results)

        return {
            "answer": answer,
            "search_results": search_results,
            "search_status": "success" if search_results else "rate_limited",
        }
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
