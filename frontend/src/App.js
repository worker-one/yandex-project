import React from 'react';
import { HashRouter, Routes, Route } from 'react-router'; // Changed import
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import IndexPage from './pages/index.js';
import ItemsTablePage from './pages/items/Table.js';
import LoginPage from './pages/auth/login.js';
import RegisterPage from './pages/auth/register.js';
import ProfilePage from './pages/auth/profile.js';
import ItemsDetailsPage from './pages/items/Details.js';
import YandexOAuthCallbackPage from './pages/auth/YandexOAuthCallbackPage.js';
import CreateItemPage from './pages/items/Create.js';

// Basic theme for Material UI
const theme = createTheme({
    palette: {
        primary: {
            main: '#272727', // Example primary color
        },
        secondary: {
            main: '#295e7c', // Example secondary color
        },
        background: {
            default: '#f5f5f5', // Light background color
            paper: '#ffffff', // Paper background color
        },
        text: {
            primary: '#242424', // Primary text color
            secondary: '#a0a0a0', // Secondary text color
        },
        mode: 'light', // Light mode by default
        sucess: {
            main: '#4caf50', // Success color
        },
    },
});

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <main>
                <Routes>
                    <Route path="/" element={<IndexPage />} />
                    <Route path="/devices" element={<ItemsTablePage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/devices/create" element={<CreateItemPage />} />
                    <Route path="/devices/:itemSerialNumber" element={<ItemsDetailsPage />} />
                    <Route path="/auth/yandex/callback" element={<YandexOAuthCallbackPage />} />
                    {/* Catch-all route for handling 404s */}
                    <Route path="*" element={<div>Page not found</div>} />
                </Routes>
            </main>
        </ThemeProvider>
    );
}

export default App;