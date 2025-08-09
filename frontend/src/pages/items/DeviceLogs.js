import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import { Container, Typography, Box, CircularProgress, Alert, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Grid } from '@mui/material';
import { getDeviceCommands, getDeviceEvents } from '../../api/devices';

const DeviceLogsPage = () => {
  const { deviceId } = useParams();
  const [commands, setCommands] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLogs = async () => {
      if (!deviceId) return;
      try {
        setLoading(true);
        setError(null);
        const [commandsData, eventsData] = await Promise.all([
          getDeviceCommands(deviceId),
          getDeviceEvents(deviceId)
        ]);
        setCommands(commandsData.commands);
        setEvents(eventsData.events);
      } catch (err) {
        setError(err.message || 'Failed to fetch device logs.');
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [deviceId]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" maxWidth="lg" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Device Logs for ID: {deviceId}
        </Typography>
        {loading && <CircularProgress />}
        {error && <Alert severity="error">{error}</Alert>}
        {!loading && !error && (
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Typography variant="h5" component="h2" gutterBottom>
                Commands
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Command Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created At</TableCell>
                      <TableCell>Completed At</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {commands.map((command) => (
                      <TableRow key={command.id}>
                        <TableCell>{command.id}</TableCell>
                        <TableCell>{command.command_type}</TableCell>
                        <TableCell>{command.status}</TableCell>
                        <TableCell>{new Date(command.created_at).toLocaleString()}</TableCell>
                        <TableCell>{command.completed_at ? new Date(command.completed_at).toLocaleString() : 'N/A'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h5" component="h2" gutterBottom>
                Events
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Event Type</TableCell>
                      <TableCell>Message</TableCell>
                      <TableCell>Created At</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {events.map((event) => (
                      <TableRow key={event.id}>
                        <TableCell>{event.id}</TableCell>
                        <TableCell>{event.event_type}</TableCell>
                        <TableCell>{event.message}</TableCell>
                        <TableCell>{new Date(event.created_at).toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        )}
      </Container>
      <Footer />
    </Box>
  );
};

export default DeviceLogsPage;
