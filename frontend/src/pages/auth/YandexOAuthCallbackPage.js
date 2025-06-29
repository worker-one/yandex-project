import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router'; // Fixed import
import { handleYandexOAuthCallback } from '../../api/auth';
import { Container, Typography, Box, CircularProgress, Alert } from '@mui/material';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';

const YandexOAuthCallbackPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const code = queryParams.get('code');
    const error = queryParams.get('error');

    // Handle OAuth error from Yandex
    if (error) {
      setError(`OAuth error: ${error}`);
      setLoading(false);
      setTimeout(() => navigate('/login?error=oauth_error'), 3000);
      return;
    }

    if (code) {
      handleYandexOAuthCallback(code)
        .then(() => {
          setLoading(false);
          // Add explicit navigation if handleYandexOAuthCallback doesn't redirect
          navigate('/');
        })
        .catch((err) => {
          console.error('OAuth callback error:', err);
          setError(err.message || 'Yandex OAuth failed. Please try again.');
          setLoading(false);
          setTimeout(() => navigate('/login?error=yandex_oauth_failed'), 3000);
        });
    } else {
      setError('No authorization code found. Redirecting to login...');
      setLoading(false);
      setTimeout(() => navigate('/login'), 3000);
    }
  }, [location, navigate]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" maxWidth="xs" sx={{ mt: 8, mb: 4, flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        {loading && (
          <>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="h6">Processing Yandex Sign-In...</Typography>
          </>
        )}
        {error && (
          <Alert severity="error" sx={{ width: '100%', mt: 2 }}>
            {error}
          </Alert>
        )}
        {!loading && !error && (
            <Alert severity="success" sx={{ width: '100%', mt: 2 }}>
                Successfully processed. Redirecting...
            </Alert>
        )}
      </Container>
      <Footer />
    </Box>
  );
};

export default YandexOAuthCallbackPage;
