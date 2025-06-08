import React from 'react';
import { Container, Typography, Link as MuiLink, Box, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router';

const Footer = () => {
  const navItems = [
    { to: '/privacy', text: 'Privacy Policy' },
    { to: '/terms', text: 'Terms of Service' },
    { to: '/about', text: 'About Us' },
    { to: '/faq', text: 'FAQ' },
    { to: '/contacts', text: 'Contacts' },
  ];

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
          © {new Date().getFullYear()} Full-Stack Template. All rights reserved.
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
          {navItems.map((item, index) => (
            <React.Fragment key={item.to}>
              <MuiLink
                component={RouterLink}
                to={item.to}
                variant="body2"
                color="text.secondary"
                sx={{ mx: 1 }} // Horizontal margin for spacing
              >
                {item.text}
              <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
              </MuiLink>
              {index < navItems.length - 1 && (
                <Typography variant="body2" component="span" color="text.secondary">
                  |
                </Typography>
              )}
            </React.Fragment>
          ))}
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;