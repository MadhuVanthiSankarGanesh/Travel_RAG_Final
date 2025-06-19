import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();
  let itinerary = location.state?.itinerary;
  let flights = location.state?.flights;
  let hotels = location.state?.hotels;
  const travelData = location.state?.travelData;

  if (!itinerary) {
    itinerary = localStorage.getItem('itinerary');
  }
  if (!flights) {
    const storedFlights = localStorage.getItem('flights');
    if (storedFlights) flights = JSON.parse(storedFlights);
  }
  if (!hotels) {
    const storedHotels = localStorage.getItem('hotels');
    if (storedHotels) hotels = JSON.parse(storedHotels);
  }

  console.log('ChatPage component rendered');
  console.log('Current URL:', window.location.href);
  console.log('Location state:', location.state);
  console.log('Itinerary from state:', itinerary);

  useEffect(() => {
    console.log('ChatPage received itinerary:', itinerary);
    console.log('ChatPage received travelData:', travelData);
    console.log('Location state:', location.state);
    console.log('Itinerary type:', typeof itinerary);
    console.log('Itinerary length:', itinerary ? itinerary.length : 'undefined');
    
    if (itinerary) {
      console.log('Setting messages with itinerary:', itinerary);
      setMessages([
        {
          role: 'assistant',
          content: `I've generated an itinerary for your trip to Ireland. Here's what I've planned:\n\n${itinerary}`
        }
      ]);
    } else {
      console.log('No itinerary received, setting default message');
      setMessages([
        {
          role: 'assistant',
          content: 'Sorry, no itinerary was generated. Please try again.'
        }
      ]);
    }
  }, [itinerary]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  // Fallback UI if no itinerary is present
  if (!itinerary || itinerary === 'undefined' || itinerary.trim() === '') {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
          <Typography variant="h5" color="error">
            No itinerary found. Please generate an itinerary first.
          </Typography>
          <Button variant="contained" color="primary" href="/travel" sx={{ mt: 2 }}>
            Go to Travel Planner
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, height: '80vh', display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Chat with Travel Assistant
        </Typography>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>Your Travel Itinerary</Typography>
          <Paper elevation={1} sx={{ p: 2, backgroundColor: 'grey.100', whiteSpace: 'pre-wrap' }}>
            {itinerary}
          </Paper>
        </Box>
        {flights && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Flight Options (Full API Response)</Typography>
            <Paper elevation={1} sx={{ p: 2, backgroundColor: 'grey.100', whiteSpace: 'pre-wrap', mb: 1 }}>
              <pre style={{ margin: 0 }}>{JSON.stringify(flights, null, 2)}</pre>
            </Paper>
            {/* Show the very first flight option if available */}
            {Array.isArray(flights.data) && flights.data.length > 0 && (
              <Paper elevation={2} sx={{ p: 2, backgroundColor: '#e3f2fd', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Top Flight Option</Typography>
                <pre style={{ margin: 0 }}>{JSON.stringify(flights.data[0], null, 2)}</pre>
              </Paper>
            )}
          </Box>
        )}
        {hotels && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Hotel Options (Full API Response)</Typography>
            <Paper elevation={1} sx={{ p: 2, backgroundColor: 'grey.100', whiteSpace: 'pre-wrap', mb: 1 }}>
              <pre style={{ margin: 0 }}>{JSON.stringify(hotels, null, 2)}</pre>
            </Paper>
            {/* Show the very first hotel option if available */}
            {Array.isArray(hotels.data) && hotels.data.length > 0 && (
              <Paper elevation={2} sx={{ p: 2, backgroundColor: '#e8f5e9', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>Top Hotel Option</Typography>
                <pre style={{ margin: 0 }}>{JSON.stringify(hotels.data[0], null, 2)}</pre>
              </Paper>
            )}
          </Box>
        )}
        <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <ListItem
                  sx={{
                    justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <Paper
                    elevation={1}
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.role === 'user' ? 'primary.light' : 'grey.100',
                      color: message.role === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <ListItemText
                      primary={message.content}
                      sx={{ whiteSpace: 'pre-wrap' }}
                    />
                  </Paper>
                </ListItem>
                {index < messages.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            sx={{ minWidth: 100 }}
          >
            {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatPage; 