import { useState } from 'react';
import { 
  Container, 
  TextField, 
  Button, 
  Box, 
  Typography, 
  Paper,
  CircularProgress,
  Link,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    background: {
      default: '#0a1929',
      paper: '#0a1929',
    },
  },
});

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/query', {
        text: query,
        context_results: 5
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box
          sx={{
            minHeight: '100vh',
            py: 4,
            display: 'flex',
            flexDirection: 'column',
            gap: 4
          }}
        >
          <Typography 
            variant="h2" 
            component="h1" 
            align="center"
            sx={{ 
              fontWeight: 'bold',
              background: 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)',
              backgroundClip: 'text',
              textFillColor: 'transparent',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Perspicuity
          </Typography>

          <Paper 
            component="form" 
            onSubmit={handleSearch}
            sx={{
              p: 2,
              display: 'flex',
              gap: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask anything..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            >
              Search
            </Button>
          </Paper>

          {error && (
            <Paper sx={{ p: 2, backgroundColor: 'rgba(255,0,0,0.1)' }}>
              <Typography color="error">{error}</Typography>
            </Paper>
          )}

          {result && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Paper sx={{ p: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace'
                  }}
                >
                  {result.answer}
                </Typography>
              </Paper>

              <Typography variant="h6" sx={{ mt: 2 }}>Sources</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {result.search_results.map((source, index) => (
                  <Paper 
                    key={index} 
                    sx={{ 
                      p: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.03)',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      }
                    }}
                  >
                    <Link 
                      href={source.link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      sx={{ color: 'primary.main', display: 'block', mb: 1 }}
                    >
                      {source.title}
                    </Link>
                    <Typography variant="body2" color="text.secondary">
                      {source.snippet}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
