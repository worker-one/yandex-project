import React from 'react';
import { Container, Typography, Link as MuiLink, Box, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router';

const Footer = () => {

  return (
    <Box
      backgroundColor="primary.main" // Using MUI's theme color
      component="footer"
      className="main-footer" // Preserving original class if needed for CSS
      sx={{
        py: 6, // Padding top and bottom
        mt: 'auto', // Pushes footer to the bottom of the page
        textAlign: 'center',
      }}
    >
      <Container maxWidth="lg" className="container"> {/* Preserving original class */}
        <Typography variant="body2" align="center" color="text.secondary">
          © {new Date().getFullYear()} Window Controller App. All rights reserved.
        </Typography>
        <Box
          component="nav"
          sx={{
            display: 'flex',
            flexWrap: 'wrap', // Allow links to wrap on smaller screens
            justifyContent: 'center',
            alignItems: 'center',
            mt: 1, // Margin top
          }}
        >
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;