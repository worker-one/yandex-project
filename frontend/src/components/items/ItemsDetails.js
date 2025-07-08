// filepath: /home/konstantin/workspace/crypta-info-react/frontend/src/components/ExchangeDetails/ExchangeInfo.js
import React from 'react';
import { Box, Typography, Grid, Paper, Link, Chip } from '@mui/material'; // Removed Avatar, Rating
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const ItemDetails = ({ item }) => {
    if (!item) return null;

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
                {/* Name */}
                <Grid item xs={12}> {/* Adjusted grid for name */}
                    <Typography variant="h4">{item.name}</Typography>
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>Details</Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                            Serial Number: {item.serial_number}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>Status:</Typography>
                            {item.capabilities.instance.on ? <CheckCircleIcon color="success" /> : <CancelIcon color="error" />}
                            {item.capabilities.instance.on ? <Typography variant="body2" sx={{ ml: 0.5 }}>Open</Typography> : <Typography variant="body2" sx={{ ml: 0.5 }}>Closed</Typography>}
                        </Box>
                        {item.last_seen && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Last Seen: {new Date(item.last_seen).toLocaleString()}
                            </Typography>
                        )}
                        {item.owner && item.owner.name && ( // Assuming owner might still be part of the fetched data if populated
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Owner: {item.owner.name}
                            </Typography>
                        )}
                         {item.owner && item.owner.email && ( // Display owner email if available
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Owner Email: <Link href={`mailto:${item.owner.email}`}>{item.owner.email}</Link>
                            </Typography>
                        )}
                        {item.created_at && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Created at: {new Date(item.created_at).toLocaleString()}
                            </Typography>
                        )}
                        {item.updated_at && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Last Updated: {new Date(item.updated_at).toLocaleString()}
                            </Typography>
                        )}
                    </Paper>
                </Grid>

            </Grid>
        </Paper>
    );
};

export default ItemDetails;