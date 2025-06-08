// filepath: /home/konstantin/workspace/crypta-info-react/frontend/src/components/ExchangeDetails/ExchangeInfo.js
import React from 'react';
import { Box, Typography, Grid, Paper, Avatar, Rating, Link, Chip } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const ItemDetails = ({ item }) => {
    if (!item) return null;

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
                <Grid item sx={{ mr: 2 }}> {/* Image */}
                    <Avatar src={item.image_url || '/assets/images/image-placeholder.png'} alt={`${item.name} Image`} sx={{ width: 56, height: 56 }} variant="rounded" />
                </Grid>

                {/* Name */}
                <Grid item xs={10} sm md={4}>
                    <Typography variant="h4">{item.name}</Typography>
                </Grid>

                {/* Rating */}
                {item.average_rating !== null && typeof item.average_rating !== 'undefined' && (
                    <Grid item xs={12} sm={6} md={3}>
                        <Rating value={parseFloat(item.average_rating) || 0} precision={0.1} readOnly />
                        {item.total_rating_count !== null && typeof item.total_rating_count !== 'undefined' && (
                            <Typography variant='caption' color="text.secondary" sx={{ ml: 1 }}>
                                ({item.total_rating_count} {item.total_rating_count === 1 ? 'review' : 'reviews'})
                            </Typography>
                        )}
                    </Grid>
                )}
            </Grid>

            {item.description && (
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Description</Typography>
                    <Typography variant="body1" dangerouslySetInnerHTML={{ __html: item.description }} />
                </Box>
            )}

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>Details</Typography>
                        {item.website_url && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Website: <Link href={item.website_url} target="_blank" rel="noopener noreferrer">{item.website_url}</Link>
                            </Typography>
                        )}
                        {typeof item.available === 'boolean' && (
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Typography variant="body2" sx={{ mr: 1 }}>Available:</Typography>
                                {item.available ? <CheckCircleIcon color="success" /> : <CancelIcon color="error" />}
                            </Box>
                        )}
                        {item.owner && item.owner.name && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Created by: {item.owner.name}
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

                {item.tags && item.tags.length > 0 && (
                    <Grid item xs={12} md={6}>
                        <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                            <Typography variant="h6" gutterBottom>Tags</Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {item.tags.map((tag, index) => (
                                    <Chip key={index} label={tag} size="small" />
                                ))}
                            </Box>
                        </Paper>
                    </Grid>
                )}
            </Grid>
        </Paper>
    );
};

export default ItemDetails;