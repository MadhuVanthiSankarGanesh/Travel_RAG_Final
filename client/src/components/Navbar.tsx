import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Travel Assistant
        </Typography>
        <Box>
          <Button
            color="inherit"
            onClick={() => navigate('/travel')}
            sx={{ 
              mx: 1,
              backgroundColor: location.pathname === '/travel' ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
            }}
          >
            Plan Trip
          </Button>
          <Button
            color="inherit"
            onClick={() => navigate('/chat')}
            sx={{ 
              mx: 1,
              backgroundColor: location.pathname === '/chat' ? 'rgba(255, 255, 255, 0.1)' : 'transparent'
            }}
          >
            Chat
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 