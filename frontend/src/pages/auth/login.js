import React, { useState } from 'react';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import { Container, Typography, Box, TextField, Button, Alert, Divider } from '@mui/material'; // Added Divider
import { handleLogin, redirectToYandexOAuth } from '../../api/auth'; // Assuming handleLogin is updated, Added redirectToYandexOAuth
// import { useNavigate } from 'react-router'; // Uncomment if using React Router

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  // const navigate = useNavigate(); // Uncomment if using React Router

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    try {
      await handleLogin(email, password);
      // handleLogin in auth.js now handles redirection via window.location.href
      // If you prefer React Router:
      // navigate('/'); // Uncomment if using React Router
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    }
  };

  const handleYandexSignIn = () => {
    redirectToYandexOAuth();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" maxWidth="xs" sx={{ mt: 8, mb: 4, flexGrow: 1 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h5">
            Sign In
          </Typography>
          {error && (
            <Alert severity="error" sx={{ width: '100%', mt: 2 }}>
              {error}
            </Alert>
          )}
          <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign In
            </Button>
            <Divider sx={{ my: 2 }}>OR</Divider>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleYandexSignIn}
              sx={{ mb: 2 }}
            >
              Sign In with Yandex
            </Button>
          </Box>
          <Typography variant="body2" color="text.secondary" align="center">
              No account? <a href="/register">Sign Up</a>
          </Typography>
        </Box>
      </Container>
      <Footer />
    </Box>
  );
};

export default LoginPage;