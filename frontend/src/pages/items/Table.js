import React, { useState } from 'react';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import { Container, Typography, Box, Button, CircularProgress, Alert } from '@mui/material';
import ItemsTable from '../../components/items/ItemsTable';
import { syncYandexIoTDevices } from '../../api/items';

const ItemsTablePage = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState(null);
  const [syncSuccess, setSyncSuccess] = useState(null);

  const handleSyncDevices = async () => {
    setSyncing(true);
    setSyncError(null);
    setSyncSuccess(null);
    try {
      const syncedItems = await syncYandexIoTDevices();
      setSyncSuccess(`Successfully synced ${syncedItems.length} device(s). Table will refresh.`);
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      setSyncError(error.message || "Failed to sync devices. Ensure you are logged in and have linked your Yandex account.");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Container component="main" maxWidth="lg" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {/* <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSyncDevices}
            disabled={syncing}
            startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {syncing ? 'Syncing...' : 'Sync Yandex Devices'}
          </Button>
        </Box> */}
        {syncError && <Alert severity="error" sx={{ mb: 2 }}>{syncError}</Alert>}
        {syncSuccess && <Alert severity="success" sx={{ mb: 2 }}>{syncSuccess}</Alert>}
        <ItemsTable refreshTrigger={refreshTrigger} />
      </Container>
      <Footer />
    </Box>
  );
};

export default ItemsTablePage;