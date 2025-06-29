import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router';
import { Container, Typography, CircularProgress, Link, Alert, Box, Button, Breadcrumbs } from '@mui/material';
import ItemDetails from '../../components/items/ItemsDetails.js';
// Assuming you have an API service for items
import { getItemDetails } from '../../api/items.js'; // Adjust the path as necessary
import Header from '../../components/common/Header.js';
import Footer from '../../components/common/Footer.js';

const ItemsDetailsPage = () => {
    const { itemSerialNumber } = useParams();
    const navigate = useNavigate();
    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchItemDetails = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getItemDetails(itemSerialNumber); // Updated function call
                setItem(data);
            } catch (err) {
                setError(err.message || 'Failed to fetch item details.');
                console.error("Error fetching item details:", err);
            } finally {
                setLoading(false);
            }
        };

        if (itemSerialNumber) {
            fetchItemDetails();
        }
    }, [itemSerialNumber]);

    if (loading) {
        return (
            <Container sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
                <CircularProgress />
            </Container>
        );
    }

    if (error) {
        return (
            <Container sx={{ mt: 5 }}>
                <Alert severity="error">{error}</Alert>
                <Button component={RouterLink} to="/items" variant="outlined" sx={{ mt: 2 }}>
                    Back to Devices
                </Button>
            </Container>
        );
    }

    if (!item) {
        return (
            <Container sx={{ mt: 5 }}>
                <Typography variant="h6">Item not found.</Typography>
                <Button component={RouterLink} to="/items" variant="outlined" sx={{ mt: 2 }}>
                    Back to Devices
                </Button>
            </Container>
        );
    }

    const breadcrumbLinks = [
        { name: 'Home', href: '/' },
        { name: 'Items', href: '/items' },
        { name: item.name || 'Details' }, // Use item name if available, otherwise 'Details'
    ];

    return (
        <>
            <Header />
            <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    
                    <Breadcrumbs aria-label="breadcrumb" sx={{ mt: 2 }}>
                        <Link component="button" onClick={() => navigate('/')} sx={{ display: 'flex', alignItems: 'center' }} color="inherit">
                            Home
                        </Link>
                        <Link component="button" onClick={() => navigate('/items')} sx={{ display: 'flex', alignItems: 'center' }} color="inherit">
                            Devices
                        </Link>
                        <Typography color="text.primary">{item.name}</Typography>
                    </Breadcrumbs>

                    <Button component={RouterLink} to="/items" variant="outlined">
                        Back to my devices
                    </Button>
                </Box>
                <ItemDetails item={item} />
            </Container>
            <Footer />
        </>
    );
};

export default ItemsDetailsPage;
