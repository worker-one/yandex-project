import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Link as MuiLink, Container, Menu, MenuItem } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router';
import { isLoggedIn, getUserProfileData, handleLogout as authHandleLogout } from '../../api/auth';

const Header = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [userName, setUserName] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const authStatus = isLoggedIn();
    setIsAuthenticated(authStatus);
    if (authStatus) {
      const userProfile = getUserProfileData();
      setIsAdmin(userProfile?.is_admin === true);
      setUserName(userProfile?.name || 'User');
    } else {
      setIsAdmin(false);
    }
  }, []);

  const onLogoutClick = () => {
    authHandleLogout();
    setIsAuthenticated(false);
    setIsAdmin(false);
    setUserName('');
    navigate('/login');
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar position="static" className="main-header">
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          
          <MuiLink
            component={RouterLink}
            to="/"
            className="logo"
            sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none', color: 'inherit' }}
            >
            <Box
              component="img"
              src="/assets/images/logo.png" 
              alt="Window Controller App Logo"
              sx={{ height: 40, mr: 1 }}
            />
            <Typography variant="h6" component="div" className="logo-text">
              Window Controller App
            </Typography>
          </MuiLink>

          <Box component="nav" id="main-nav" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {!isAuthenticated ? (
              <>
                <Button
                  component={RouterLink}
                  to="/login" 
                  variant="contained" 
                  color="secondary" 
                  size="small"
                  id="nav-login-btn" 
                  sx={{ color: 'white' }} 
                >
                  Sign In
                </Button>
              </>
            ) : (
              <>
                <Typography sx={{ mr: 2 }}>
                  {userName}
                </Typography>
                <Button
                  color="inherit"
                  onClick={handleMenuOpen}
                >
                  My Devices
                </Button>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem component={RouterLink} to="/devices" onClick={handleMenuClose}>All Devices</MenuItem>
                  <MenuItem component={RouterLink} to="/devices/create" onClick={handleMenuClose}>Add Device</MenuItem>
                </Menu>
                <Button
                  component={RouterLink}
                  to="/logs"
                  color="inherit"
                  className="nav-link"
                >
                  Logs
                </Button>
                <Button
                  component={RouterLink}
                  to="/profile" 
                  color="inherit"
                  className="nav-link" 
                  id="nav-profile-link" 
                >
                  My Profile
                </Button>
                {isAdmin && (
                  <Button
                    component={RouterLink}
                    to="/admin" 
                    color="inherit"
                    className="nav-link" 
                    id="nav-admin-link" 
                  >
                    Admin Panel
                  </Button>
                )}
                <Button
                  variant="contained" 
                  color="secondary" 
                  id="nav-logout-btn" 
                  onClick={onLogoutClick} 
                >
                  Sign Out
                </Button>
              </>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;