import React, { useState } from 'react';
import { useNavigate } from 'react-router';
import { Button, Box, CircularProgress, TextField, Typography, Alert } from '@mui/material';
import { createDevice } from '../../api/items';

const CreateForm = () => {
    const [deviceData, setDeviceData] = useState({
        name: '',
        serial_number: '',
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (event) => {
        const { name, value } = event.target;
        setDeviceData(prevState => ({
            ...prevState,
            [name]: value,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError(null);

        // Filter out empty optional fields
        const dataToSubmit = { ...deviceData };
        for (const key in dataToSubmit) {
            if (dataToSubmit[key] === '') {
                delete dataToSubmit[key];
            }
        }

        try {
            const newDevice = await createDevice(dataToSubmit);
            navigate(`/devices/${newDevice.serial_number}`);
        } catch (err) {
            setError(err.message || 'An error occurred while creating the device.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Add New Device
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField
                margin="normal"
                required
                fullWidth
                id="name"
                label="Device Name"
                name="name"
                autoComplete="name"
                autoFocus
                value={deviceData.name}
                onChange={handleChange}
            />
            <TextField
                margin="normal"
                required
                fullWidth
                id="serial_number"
                label="Serial Number"
                name="serial_number"
                value={deviceData.custom_data.serial_number}
                onChange={handleChange}
                helperText="Enter the serial number of the device"
            />
            <Button
                type="submit"
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
            >
                {loading ? <CircularProgress size={24} /> : 'Add Device'}
            </Button>
        </Box>
    );
};

export default CreateForm;