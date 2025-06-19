import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  MenuItem,
  Box,
  CircularProgress,
  Autocomplete,
  Chip,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// List of Irish counties
const IRISH_COUNTIES = [
  "Antrim", "Armagh", "Carlow", "Cavan", "Clare", "Cork", "Derry", "Donegal",
  "Down", "Dublin", "Fermanagh", "Galway", "Kerry", "Kildare", "Kilkenny",
  "Laois", "Leitrim", "Limerick", "Longford", "Louth", "Mayo", "Meath",
  "Monaghan", "Offaly", "Roscommon", "Sligo", "Tipperary", "Tyrone",
  "Waterford", "Westmeath", "Wexford", "Wicklow"
];

// List of major European airports
const EUROPEAN_AIRPORTS = [
  { code: "LHR", name: "London Heathrow", city: "London", country: "United Kingdom" },
  { code: "CDG", name: "Paris Charles de Gaulle", city: "Paris", country: "France" },
  { code: "AMS", name: "Amsterdam Schiphol", city: "Amsterdam", country: "Netherlands" },
  { code: "FRA", name: "Frankfurt International", city: "Frankfurt", country: "Germany" },
  { code: "MAD", name: "Madrid Barajas", city: "Madrid", country: "Spain" },
  { code: "BCN", name: "Barcelona El Prat", city: "Barcelona", country: "Spain" },
  { code: "FCO", name: "Rome Fiumicino", city: "Rome", country: "Italy" },
  { code: "MXP", name: "Milan Malpensa", city: "Milan", country: "Italy" },
  { code: "ZRH", name: "Zurich Airport", city: "Zurich", country: "Switzerland" },
  { code: "VIE", name: "Vienna International", city: "Vienna", country: "Austria" },
  { code: "BRU", name: "Brussels Airport", city: "Brussels", country: "Belgium" },
  { code: "CPH", name: "Copenhagen Airport", city: "Copenhagen", country: "Denmark" },
  { code: "ARN", name: "Stockholm Arlanda", city: "Stockholm", country: "Sweden" },
  { code: "OSL", name: "Oslo Gardermoen", city: "Oslo", country: "Norway" },
  { code: "HEL", name: "Helsinki Airport", city: "Helsinki", country: "Finland" },
  { code: "WAW", name: "Warsaw Chopin", city: "Warsaw", country: "Poland" },
  { code: "PRG", name: "Prague Václav Havel", city: "Prague", country: "Czech Republic" },
  { code: "BUD", name: "Budapest Ferenc Liszt", city: "Budapest", country: "Hungary" },
  { code: "IST", name: "Istanbul Airport", city: "Istanbul", country: "Turkey" },
  { code: "ATH", name: "Athens International", city: "Athens", country: "Greece" },
  { code: "LIS", name: "Lisbon Portela", city: "Lisbon", country: "Portugal" },
  { code: "OPO", name: "Porto Airport", city: "Porto", country: "Portugal" },
  { code: "DUB", name: "Dublin Airport", city: "Dublin", country: "Ireland" },
  { code: "EDI", name: "Edinburgh Airport", city: "Edinburgh", country: "United Kingdom" },
  { code: "MAN", name: "Manchester Airport", city: "Manchester", country: "United Kingdom" },
  { code: "GLA", name: "Glasgow International", city: "Glasgow", country: "United Kingdom" },
  { code: "BHX", name: "Birmingham Airport", city: "Birmingham", country: "United Kingdom" },
  { code: "NCE", name: "Nice Côte d'Azur", city: "Nice", country: "France" },
  { code: "MUC", name: "Munich Airport", city: "Munich", country: "Germany" },
  { code: "BER", name: "Berlin Brandenburg", city: "Berlin", country: "Germany" }
];

interface TravelData {
  origin_country: string;
  arrival_date: string;
  departure_date: string;
  adults: number;
  children: number;
  travel_class: string;
  interests: string[];
  budget: string;
  preferred_counties: string[];
  accommodation_type: string;
  transportation: string;
  dietary_restrictions: string[];
  accessibility_needs: boolean;
  special_requests: string;
}

const TravelPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<TravelData>({
    origin_country: '',
    arrival_date: '',
    departure_date: '',
    adults: 1,
    children: 0,
    travel_class: 'ECONOMY',
    interests: [],
    budget: 'medium',
    preferred_counties: [],
    accommodation_type: 'hotel',
    transportation: 'rental car',
    dietary_restrictions: [],
    accessibility_needs: false,
    special_requests: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Create an AbortController with a longer timeout (5 minutes)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000); // 5 minutes

      const response = await fetch('/api/travel/generate-itinerary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 504) {
          throw new Error('Request timed out. The itinerary generation is taking longer than expected. Please try again.');
        }
        throw new Error(`Failed to generate itinerary: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('API Response:', result);
      console.log('Itinerary being passed:', result.itinerary);
      
      if (!result.itinerary) {
        alert('No itinerary was generated. Please try again.');
        return;
      }
      localStorage.setItem('itinerary', result.itinerary);
      if (result.flights) localStorage.setItem('flights', JSON.stringify(result.flights));
      if (result.hotels) localStorage.setItem('hotels', JSON.stringify(result.hotels));
      navigate('/chat', { state: { itinerary: result.itinerary, flights: result.flights, hotels: result.hotels, travelData: formData } });
    } catch (error: any) {
      console.error('Error:', error);
      if (error.name === 'AbortError') {
        alert('Request timed out. The itinerary generation is taking longer than expected. Please try again.');
      } else {
        alert(error.message || 'An error occurred while generating the itinerary');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof TravelData) => (
    e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>
  ) => {
    const value = e.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDateChange = (field: 'arrival_date' | 'departure_date') => (date: Date | null) => {
    if (date) {
      setFormData(prev => ({
        ...prev,
        [field]: date.toISOString().split('T')[0]
      }));
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Plan Your Ireland Trip
        </Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Autocomplete
                id="airport-select"
                options={EUROPEAN_AIRPORTS}
                getOptionLabel={(option) => `${option.name} (${option.code}) - ${option.city}, ${option.country}`}
                value={EUROPEAN_AIRPORTS.find(airport => airport.code === formData.origin_country) || null}
                onChange={(_, newValue) => {
                  setFormData(prev => ({
                    ...prev,
                    origin_country: newValue ? newValue.code : ''
                  }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Departure Airport"
                    required
                    placeholder="Select your departure airport"
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: 'primary.main',
                        },
                        '&:hover fieldset': {
                          borderColor: 'primary.dark',
                        },
                      },
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box sx={{ py: 0.5 }}>
                      <Typography variant="body1" component="div">
                        <strong>{option.name}</strong> ({option.code})
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {option.city}, {option.country}
                      </Typography>
                    </Box>
                  </li>
                )}
                groupBy={(option) => option.country}
                sx={{
                  '& .MuiAutocomplete-input': {
                    padding: '10.5px 14px !important'
                  },
                  '& .MuiAutocomplete-popper': {
                    zIndex: 1300
                  },
                  '& .MuiAutocomplete-groupLabel': {
                    backgroundColor: 'background.paper',
                    color: 'primary.main',
                    fontWeight: 'bold',
                    padding: '8px 16px'
                  }
                }}
                ListboxProps={{
                  sx: {
                    maxHeight: '400px',
                    '& .MuiAutocomplete-option': {
                      padding: '8px 16px'
                    }
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Arrival Date"
                  value={formData.arrival_date ? new Date(formData.arrival_date) : null}
                  onChange={handleDateChange('arrival_date')}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      required: true
                    }
                  }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} md={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Departure Date"
                  value={formData.departure_date ? new Date(formData.departure_date) : null}
                  onChange={handleDateChange('departure_date')}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      required: true
                    }
                  }}
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Adults"
                value={formData.adults}
                onChange={handleChange('adults')}
                inputProps={{ min: 1, max: 9 }}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Children"
                value={formData.children}
                onChange={handleChange('children')}
                inputProps={{ min: 0, max: 9 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Travel Class"
                value={formData.travel_class}
                onChange={handleChange('travel_class')}
                required
              >
                <MenuItem value="ECONOMY">Economy</MenuItem>
                <MenuItem value="PREMIUM_ECONOMY">Premium Economy</MenuItem>
                <MenuItem value="BUSINESS">Business</MenuItem>
                <MenuItem value="FIRST">First</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={IRISH_COUNTIES}
                value={formData.preferred_counties}
                onChange={(_, newValue) => {
                  setFormData(prev => ({
                    ...prev,
                    preferred_counties: newValue
                  }));
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Preferred Counties to Visit"
                    placeholder="Select counties"
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Special Requirements"
                value={formData.special_requests}
                onChange={handleChange('special_requests')}
                placeholder="Tell us about any special requirements or preferences..."
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={isLoading}
                  sx={{ minWidth: 200 }}
                >
                  {isLoading ? (
                    <>
                      <CircularProgress size={24} sx={{ mr: 1 }} />
                      Generating Itinerary... (This may take 1-2 minutes)
                    </>
                  ) : (
                    'Generate Itinerary'
                  )}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default TravelPage; 