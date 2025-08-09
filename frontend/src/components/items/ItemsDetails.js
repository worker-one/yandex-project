// filepath: /home/konstantin/workspace/crypta-info-react/frontend/src/components/ExchangeDetails/ExchangeInfo.js
import React, { useState } from 'react';
import { Box, Typography, Grid, Paper, Link, Chip, TextField, Button, Alert } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

const ItemDetails = ({ item, onMqttSettingsUpdate, onDeviceUnlink }) => {
    const [mqttSettings, setMqttSettings] = useState(item?.mqtt_settings || {
        address: '83.217.223.59:1883',
        username: 'mosquitto_user',
        password: 'mosquitto_password'
    });
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState(null);

    if (!item) return null;

    const batteryLevel = item.capabilities?.find(c => c.type === 'devices.capabilities.range' && c.parameters.instance === 'battery_level')?.state.value;

    const handleSaveMqttSettings = async () => {
        setIsLoading(true);
        setMessage(null);
        try {
            if (onMqttSettingsUpdate) {
                await onMqttSettingsUpdate(item.id, mqttSettings);
                setMessage({ type: 'success', text: 'MQTT settings saved successfully!' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to save MQTT settings.' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleUnlinkDevice = async (deviceId) => {
        setIsLoading(true);
        setMessage(null);
        try {
            if (onDeviceUnlink) {
                await onDeviceUnlink(deviceId);
                setMessage({ type: 'success', text: 'Device unlinked successfully!' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to unlink device.' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
            {message && (
                <Alert severity={message.type} sx={{ mb: 2 }}>
                    {message.text}
                </Alert>
            )}
            
            <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
                <Grid item xs={12}>
                    <Typography variant="h4">{item.name}</Typography>
                </Grid>
            </Grid>

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                        <Typography variant="h6" gutterBottom>Device Information</Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                            Serial Number: {item.serial_number}
                        </Typography>
                        {batteryLevel !== undefined && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Battery Level: {batteryLevel}%
                            </Typography>
                        )}
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>Status:</Typography>
                            {item.status === "on" ? <CheckCircleIcon color="success" /> : <CancelIcon color="error" />}
                            <Typography variant="body2" sx={{ ml: 0.5 }}>
                                {item.status === "on" ? "Online" : "Offline"}
                            </Typography>
                        </Box>
                        {item.last_seen && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Last Seen: {new Date(item.last_seen).toLocaleString()}
                            </Typography>
                        )}
                        {item.owner && item.owner.name && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Owner: {item.owner.name}
                            </Typography>
                        )}
                        {item.owner && item.owner.email && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Email: <Link href={`mailto:${item.owner.email}`}>{item.owner.email}</Link>
                            </Typography>
                        )}
                        {item.created_at && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Created: {new Date(item.created_at).toLocaleString()}
                            </Typography>
                        )}
                        {item.updated_at && (
                            <Typography variant="body2" sx={{ mb: 1 }}>
                                Last Updated: {new Date(item.updated_at).toLocaleString()}
                            </Typography>
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                        <Typography variant="h6" gutterBottom>MQTT Settings</Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="MQTT Broker Address"
                                    value={mqttSettings.address}
                                    helperText="Format: hostname:port"
                                    onChange={(e) => setMqttSettings({ ...mqttSettings, address: e.target.value })}
                                    disabled={isLoading}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="MQTT Username"
                                    value={mqttSettings.username}
                                    onChange={(e) => setMqttSettings({ ...mqttSettings, username: e.target.value })}
                                    disabled={isLoading}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="MQTT Password"
                                    type="password"
                                    value={mqttSettings.password}
                                    onChange={(e) => setMqttSettings({ ...mqttSettings, password: e.target.value })}
                                    disabled={isLoading}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    onClick={handleSaveMqttSettings}
                                    disabled={isLoading}
                                    fullWidth
                                >
                                    {isLoading ? 'Saving...' : 'Save MQTT Settings'}
                                </Button>
                            </Grid>
                        </Grid>
                    </Paper>

                    <Paper variant="outlined" sx={{ p: 2 }}>
                        <Button
                            variant="outlined"
                            color="error"
                            onClick={() => handleUnlinkDevice(item.id)}
                            disabled={isLoading}
                            fullWidth
                        >
                            {isLoading ? 'Unlinking...' : 'Unlink Device'}
                        </Button>
                    </Paper>
                </Grid>
            </Grid>
        </Paper>
    );
};

export default ItemDetails;