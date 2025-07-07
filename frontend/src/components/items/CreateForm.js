import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import {
    Box,
    TextField,
    Button,
    Typography,
    Paper,
    Alert,
    CircularProgress
} from '@mui/material';
import { createDevice } from '../../api/devices.js';

const CreateForm = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        serial_number: '',
        room: 'main'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await createDevice(formData);
            navigate('/devices');
        } catch (err) {
            setError(err.message || 'Failed to create device');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Create New Device
            </Typography>
            
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                <TextField
                    fullWidth
                    label="Device Name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    margin="normal"
                />
                
                <TextField
                    fullWidth
                    label="Serial Number"
                    name="serial_number"
                    value={formData.serial_number}
                    onChange={handleChange}
                    required
                    margin="normal"
                />
                
                <TextField
                    fullWidth
                    label="Room"
                    name="room"
                    value={formData.room}
                    onChange={handleChange}
                    margin="normal"
                    helperText="Specify which room this device belongs to"
                />

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                    <Button
                        type="submit"
                        variant="contained"
                        disabled={loading}
                        startIcon={loading && <CircularProgress size={20} />}
                    >
                        {loading ? 'Creating...' : 'Create Device'}
                    </Button>
                    
                    <Button
                        variant="outlined"
                        onClick={() => navigate('/devices')}
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                </Box>
            </Box>
        </Paper>
    );
};

export default CreateForm;