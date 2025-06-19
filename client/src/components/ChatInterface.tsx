import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  Card,
  CardContent,
  Grid
} from '@mui/material';
import { TravelData } from '../types';

interface Message {
  text: string;
  isUser: boolean;
  itinerary?: string;
  flightResults?: any;
  hotelResults?: any;
}

interface ChatInterfaceProps {
  travelData?: TravelData;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ travelData }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          travel_data: travelData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        text: data.response,
        isUser: false,
        itinerary: data.itinerary,
        flightResults: data.flight_results,
        hotelResults: data.hotel_results
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: Message) => {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: message.isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            backgroundColor: message.isUser ? 'primary.light' : 'grey.100',
            color: message.isUser ? 'white' : 'text.primary',
          }}
        >
          <Typography variant="body1">{message.text}</Typography>
          
          {message.itinerary && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>Your Travel Itinerary</Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                {message.itinerary}
              </Typography>
            </Box>
          )}

          {message.flightResults && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>Flight Options</Typography>
              <List>
                {message.flightResults.data?.map((flight: any, index: number) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`${flight.itineraries[0].segments[0].departure.iataCode} → ${flight.itineraries[0].segments[0].arrival.iataCode}`}
                      secondary={`Price: ${flight.price.total} ${flight.price.currency}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {message.hotelResults && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>Hotel Options</Typography>
              <Grid container spacing={2}>
                {message.hotelResults.data?.map((hotel: any, index: number) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6">{hotel.hotel.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {hotel.hotel.rating} stars
                        </Typography>
                        <Typography variant="body2">
                          Price: {hotel.offers[0].price.total} {hotel.offers[0].price.currency}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {messages.map((message, index) => (
          <React.Fragment key={index}>
            {renderMessage(message)}
          </React.Fragment>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>
      <Divider />
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 2,
          backgroundColor: 'background.paper',
          display: 'flex',
          gap: 1,
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={isLoading || !input.trim()}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface; 