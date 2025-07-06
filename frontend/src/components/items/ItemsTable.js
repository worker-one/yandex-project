import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  TableSortLabel, TablePagination, CircularProgress, Typography, Box, Button, Link as MuiLink // Removed Chip
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router';
import { getUserDevices as fetchUserDevicesAPI } from '../../api/devices'; // Use correct API function

const DEFAULT_ROWS_PER_PAGE = 20;

const headCells = [
  { id: 'index', numeric: true, disablePadding: false, label: '#', sortable: false, align: 'center' },
  { id: 'name', numeric: false, disablePadding: false, label: 'Name', sortable: true, align: 'left' },
  { id: 'serial_number', numeric: false, disablePadding: false, label: 'Serial Number', sortable: true, align: 'left' },
  { id: 'owner', numeric: false, disablePadding: false, label: 'Owner', sortable: false, align: 'left' },
  { id: 'actions', numeric: false, disablePadding: false, label: 'Actions', sortable: false, align: 'center' },
];


const DevicesTable = ({ refreshTrigger }) => { // Add refreshTrigger to props
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [order, setOrder] = useState('desc');
  const [orderBy, setOrderBy] = useState('name'); // Default sort by name
  const [page, setPage] = useState(0); // 0-indexed
  const [rowsPerPage, setRowsPerPage] = useState(DEFAULT_ROWS_PER_PAGE);
  const [totalRows, setTotalRows] = useState(0);
  const navigate = useNavigate();

  const fetchDevices = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        // Filtering and sorting for user devices endpoint is limited; ignore sort for now
      };
      // Remove undefined or null params
      Object.keys(params).forEach(key => (params[key] == null) && delete params[key]);
      console.log('[DevicesTable] Fetching user devices with params:', params);
      const data = await fetchUserDevicesAPI(params); // Use imported API function
      console.log('[DevicesTable] Received devices data:', data);
      setDevices(data.devices || []);
      setTotalRows(data.total || 0);
    } catch (err) {
      console.error('[DevicesTable] Error fetching devices:', err);
      setError(err.message);
      setDevices([]);
      setTotalRows(0);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices, refreshTrigger]); // Add refreshTrigger to dependency array

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
    setPage(0); // Reset to first page on sort
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset to first page on rows per page change
  };

  const handleRowClick = (event, serialNumber) => {
    // Prevent navigation if the click was on a link or button inside the row
    if (event.target.closest('a, button')) {
      return;
    }
    navigate(`/devices/${serialNumber}`);
  };

  if (loading) {
    return <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}><CircularProgress /></Box>;
  }

  if (error) {
    return <Typography color="error" sx={{ p: 3 }}>Error loading devices: {error}</Typography>;
  }

  return (
    <Paper sx={{ width: '100%', mb: 2 }}>
      <TableContainer>
        <Table stickyHeader aria-label="devices table">
          <TableHead>
            <TableRow>
              {headCells.map((headCell) => (
                <TableCell
                  key={headCell.id}
                  align={headCell.align || (headCell.numeric ? 'right' : 'left')}
                  padding={headCell.disablePadding ? 'none' : 'normal'}
                  sortDirection={orderBy === headCell.id ? order : false}
                  sx={{ 
                    fontWeight: 'bold',
                    ...(headCell.id === 'index' && { width: '5%' }),
                    ...(headCell.id === 'name' && { width: '20%' }),
                    ...(headCell.id === 'serial_number' && { width: '20%' }),
                    ...(headCell.id === 'owner' && { width: '20%' }),
                    ...(headCell.id === 'actions' && { width: '15%' })
                  }}
                >
                  {headCell.sortable ? (
                    <TableSortLabel
                      active={orderBy === headCell.id}
                      direction={orderBy === headCell.id ? order : 'asc'}
                      onClick={() => handleRequestSort(headCell.id)}
                    >
                      {headCell.label}
                    </TableSortLabel>
                  ) : (
                    headCell.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {devices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={headCells.length} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                  No devices found.
                </TableCell>
              </TableRow>
            ) : (
              devices.map((device, index) => {
                const startIndex = page * rowsPerPage;
                return (
                  <TableRow
                    hover
                    key={device.id}
                    onClick={(event) => handleRowClick(event, device.serial_number)}
                    sx={{ cursor: 'pointer' }}
                  >
                    {/* Index */}
                    <TableCell align="center">
                      {startIndex + index + 1}
                    </TableCell>

                    {/* Name */}
                    <TableCell align="left">
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {device.name || 'N/A'}
                      </Typography>
                    </TableCell>

                    {/* Serial Number */}
                    <TableCell align="left">
                      <Typography variant="body2">
                        {device.serial_number || 'N/A'}
                      </Typography>
                    </TableCell>

                    {/* Owner */}
                    <TableCell align="left">
                      <Typography variant="body2">
                        {device.owner ? device.owner.email || device.owner.username || 'N/A' : 'N/A'}
                      </Typography>
                    </TableCell>

                    {/* Actions */}
                    <TableCell align="center">
                      <Button
                        component={RouterLink}
                        to={`/devices/${device.serial_number}`}
                        variant="outlined"
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                        sx={{ minWidth: 'auto', px: 2 }}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 20, 50]}
        component="div"
        count={totalRows}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Rows on the page:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} / ${count !== -1 ? count : `больше чем ${to}`}`}
      />
    </Paper>
  );
};

export default DevicesTable;