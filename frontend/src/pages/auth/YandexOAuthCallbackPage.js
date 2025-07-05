import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import { handleYandexOAuthCallback, clearAuthData } from '../../api/auth'; // Import shared logic

const YandexOAuthCallbackPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const handleOAuthCallback = async () => {
            const code = searchParams.get('code');
            const cid = searchParams.get('cid');
            
            if (!code) {
                setError('Authorization code not found');
                setLoading(false);
                return;
            }

            try {
                // Use shared API logic to process Yandex OAuth callback and store tokens/profile
                await handleYandexOAuthCallback(code);
                // Redirect to home/dashboard after successful login
                navigate('/', { replace: true });
            } catch (err) {
                console.error('OAuth callback error:', err);
                setError(err.message || 'Authentication failed');
                setLoading(false);
            }
        };

        handleOAuthCallback();
    }, [searchParams, navigate]);

    if (loading) {
        return (
            <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                minHeight="100vh"
                gap={2}
            >
                <CircularProgress />
                <Typography variant="h6">
                    Completing Yandex authentication...
                </Typography>
            </Box>
        );
    }

    if (error) {
        console.error('OAuth error:', error);
        clearAuthData(); // Use shared logout logic
        return (
            <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                minHeight="100vh"
                gap={2}
                padding={3}
            >
                <Alert severity="error" sx={{ maxWidth: 400 }}>
                    <Typography variant="h6" gutterBottom>
                        Authentication Failed
                    </Typography>
                    <Typography>
                        {error}
                    </Typography>
                </Alert>
                <Typography 
                    variant="body2" 
                    color="primary" 
                    sx={{ cursor: 'pointer', textDecoration: 'underline' }}
                    onClick={() => navigate('/login')}
                >
                    Return to login
                </Typography>
            </Box>
        );
    }

    return null; // This shouldn't be reached
};

export default YandexOAuthCallbackPage;
