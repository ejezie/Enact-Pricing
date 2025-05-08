import { useState } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  Avatar,
  CircularProgress,
  Divider,
} from '@mui/material';
import { Send as SendIcon, SmartToy as BotIcon } from '@mui/icons-material';
import { ChatMessage } from '../types';

interface AIAssistantProps {
  data: any; // The market data context for the AI
}

export default function AIAssistant({ data }: AIAssistantProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I can help you analyze the market data. What would you like to know?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          context: data,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const result = await response.json();
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper elevation={0} sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'primary.contrastText' }}>
        <Typography variant="h6">
          AI Market Analysis Assistant
        </Typography>
      </Box>

      <List sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 2,
        backgroundColor: 'grey.50',
      }}>
        {messages.map((message, index) => (
          <ListItem
            key={index}
            sx={{
              flexDirection: 'column',
              alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'flex-start',
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
              gap: 1,
              maxWidth: '80%',
            }}>
              <Avatar
                sx={{
                  bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                  width: 32,
                  height: 32,
                }}
              >
                {message.role === 'user' ? 'U' : <BotIcon />}
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  backgroundColor: message.role === 'user' ? 'primary.main' : 'white',
                  color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: 2,
                }}
              >
                <Typography variant="body1">
                  {message.content}
                </Typography>
                <Typography
                  variant="caption"
                  color={message.role === 'user' ? 'primary.light' : 'text.secondary'}
                  sx={{ display: 'block', mt: 1 }}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          </ListItem>
        ))}
        {isLoading && (
          <ListItem>
            <CircularProgress size={20} />
          </ListItem>
        )}
      </List>

      <Divider />

      <Box sx={{ p: 2, backgroundColor: 'background.paper' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about market trends, pricing strategies, or competitor analysis..."
            variant="outlined"
            size="small"
          />
          <Button
            variant="contained"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            sx={{ minWidth: 100 }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              <>
                Send
                <SendIcon sx={{ ml: 1 }} />
              </>
            )}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
} 