import React, { useState, KeyboardEvent, ChangeEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { TravelData } from '../types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const Chat: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { itinerary, travelData } = location.state as { itinerary: string; travelData: TravelData };
  
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: itinerary }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user' as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          travelData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          mb: 2, 
          p: 2, 
          overflow: 'auto',
          backgroundColor: 'background.paper'
        }}
      >
        {travelData.dailyItinerary && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              Your Ireland Itinerary
            </Typography>
            {travelData.dailyItinerary.map((day, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>
                    Day {index + 1} - {formatDate(day.date)} - {day.county}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    <ListItem>
                      <ListItemText 
                        primary="Morning"
                        secondary={day.activities.morning}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText 
                        primary="Afternoon"
                        secondary={day.activities.afternoon}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText 
                        primary="Evening"
                        secondary={day.activities.evening}
                      />
                    </ListItem>
                    {day.accommodation && (
                      <>
                        <Divider />
                        <ListItem>
                          <ListItemText 
                            primary="Accommodation"
                            secondary={`${day.accommodation.type} in ${day.accommodation.location}
                              Check-in: ${formatDate(day.accommodation.checkIn)}
                              Check-out: ${formatDate(day.accommodation.checkOut)}`}
                          />
                        </ListItem>
                      </>
                    )}
                  </List>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}

        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                backgroundColor: message.role === 'user' ? 'primary.light' : 'grey.100',
                color: message.role === 'user' ? 'white' : 'text.primary'
              }}
            >
              <Typography variant="body1">{message.content}</Typography>
            </Paper>
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Paper>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask about your itinerary..."
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          multiline
          maxRows={4}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSendMessage}
          disabled={isLoading || !input.trim()}
          endIcon={<SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default Chat; 