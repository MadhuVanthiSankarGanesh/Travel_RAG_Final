import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  MenuItem,
  TextField,
  Grid,
  Chip,
  OutlinedInput,
  SelectChangeEvent,
  Typography,
  Paper,
  InputLabel,
  CircularProgress,
  Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { TravelData, EUROPEAN_COUNTRIES, IRISH_COUNTIES, INTERESTS } from '../types';

interface TravelFormProps {
  onSubmit: (data: TravelData) => void;
}

const TravelForm: React.FC<TravelFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<TravelData>({
    originCountry: '',
    destinationCountry: 'IE',
    arrivalDate: undefined,
    departureDate: undefined,
    adults: 1,
    children: [],
    budget: 0,
    travelClass: 'ECONOMY',
    interests: INTERESTS,
    selectedInterests: [],
    countiesToVisit: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }> | SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name as string]: value
    }));
  };

  const handleDateChange = (field: keyof TravelData) => (date: Date | null) => {
    setFormData(prev => ({
      ...prev,
      [field]: date || undefined
    }));
  };

  const handleMultiSelect = (e: SelectChangeEvent<string[]>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name as string]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating the itinerary');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Plan Your Ireland Trip
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Origin Country</InputLabel>
              <Select
                name="originCountry"
                value={formData.originCountry}
                onChange={handleInputChange}
                label="Origin Country"
                required
              >
                {EUROPEAN_COUNTRIES.map((country) => (
                  <MenuItem key={country.code} value={country.code}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Destination Country</InputLabel>
              <Select
                name="destinationCountry"
                value={formData.destinationCountry}
                onChange={handleInputChange}
                label="Destination Country"
                required
              >
                {EUROPEAN_COUNTRIES.map((country) => (
                  <MenuItem key={country.code} value={country.code}>
                    {country.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Arrival Date"
                value={formData.arrivalDate}
                onChange={handleDateChange('arrivalDate')}
                sx={{ width: '100%' }}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Departure Date"
                value={formData.departureDate}
                onChange={handleDateChange('departureDate')}
                sx={{ width: '100%' }}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Number of Adults"
              name="adults"
              value={formData.adults}
              onChange={handleInputChange}
              inputProps={{ min: 1 }}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Travel Class</InputLabel>
              <Select
                name="travelClass"
                value={formData.travelClass}
                onChange={handleInputChange}
                label="Travel Class"
              >
                <MenuItem value="ECONOMY">Economy</MenuItem>
                <MenuItem value="PREMIUM_ECONOMY">Premium Economy</MenuItem>
                <MenuItem value="BUSINESS">Business</MenuItem>
                <MenuItem value="FIRST">First</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="number"
              label="Budget (EUR)"
              name="budget"
              value={formData.budget}
              onChange={handleInputChange}
              inputProps={{ min: 0, step: 100 }}
              required
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Counties to Visit</InputLabel>
              <Select
                multiple
                name="countiesToVisit"
                value={formData.countiesToVisit}
                onChange={handleMultiSelect}
                input={<OutlinedInput label="Counties to Visit" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                {IRISH_COUNTIES.map((county) => (
                  <MenuItem key={county} value={county}>
                    {county}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Interests</InputLabel>
              <Select
                multiple
                name="selectedInterests"
                value={formData.selectedInterests}
                onChange={handleMultiSelect}
                input={<OutlinedInput label="Interests" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                {INTERESTS.map((interest) => (
                  <MenuItem key={interest} value={interest}>
                    {interest}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={isLoading}
              sx={{ mt: 2 }}
            >
              {isLoading ? (
                <>
                  <CircularProgress size={24} sx={{ mr: 1 }} />
                  Generating Itinerary...
                </>
              ) : (
                'Generate Itinerary'
              )}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default TravelForm; 