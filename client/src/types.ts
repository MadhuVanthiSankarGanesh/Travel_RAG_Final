export interface ConversationMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export interface ChatRequest {
    content: string;
    conversation_history: Array<{
        role: string;
        content: string;
    }>;
}

export interface ChatResponse {
    response: string;
    itinerary?: {
        destination: string;
        duration: number;
        suggested_activities: string[];
        accommodation: {
            check_in: string;
            check_out: string;
        };
        flights: {
            departure: string;
            return: string;
        };
    };
    travel_info?: {
        origin?: string;
        destination?: string;
        dates?: {
            departure: string;
            return: string;
        };
        duration?: number;
        travelers?: number;
    };
}

export interface ApiError {
    detail: string;
}

export interface ChatInputProps {
    onSendMessage: (message: string) => void;
    isLoading: boolean;
}

export interface ChatMessageProps {
    message: ConversationMessage;
}

export interface TravelData {
    // Basic Travel Info
    originCountry: string;
    destinationCountry: string;
    arrivalDate: Date | undefined;
    departureDate: Date | undefined;
    adults: number;
    children: number[];
    budget: number;
    travelClass: 'ECONOMY' | 'PREMIUM_ECONOMY' | 'BUSINESS' | 'FIRST';
    
    // Interests and Preferences
    interests: string[];
    selectedInterests: string[];
    countiesToVisit: string[];
    
    // Generated Itinerary (will be populated by LLM)
    dailyItinerary?: {
        date: Date;
        county: string;
        activities: {
            morning: string;
            afternoon: string;
            evening: string;
        };
        accommodation?: {
            location: string;
            checkIn: Date;
            checkOut: Date;
            type: string;
        };
    }[];
    
    // Flight Details (will be populated by LLM)
    flightDetails?: {
        airline: string;
        departureTime: Date;
        arrivalTime: Date;
        price: number;
    };
}

export interface FlightOption {
    status: boolean;
    message?: {
        message: string;
        code: string;
    };
    data?: {
        flights: Array<{
            airline: string;
            departure_time: string;
            arrival_time: string;
            price_eur: number;
        }>;
    };
}

export interface HotelOption {
    status: boolean;
    message?: {
        message: string;
        code: string;
    };
    data?: {
        hotels: Array<{
            city: string;
            hotel_name: string;
            check_in: string;
            check_out: string;
            price_per_night_eur: number;
            total_price_eur: number;
        }>;
    };
}

export interface ItineraryRequest {
    travelData: TravelData;
    flightOptions: FlightOption;
    hotelOptions: HotelOption;
}

export interface TripSummary {
    origin_airport: string;
    destination_airport: string;
    departure_date: string;
    return_date: string;
    number_of_adults: number;
    number_of_children: number;
    total_days: number;
    estimated_total_cost_eur: number;
    transport_mode: string;
}

export interface DailyItinerary {
    day: number;
    date: string;
    location: string;
    activities: {
        morning: string;
        afternoon: string;
        evening: string;
    };
    hotel: string;
}

export interface BudgetBreakdown {
    flights: number;
    hotels: number;
    activities_and_tickets: number;
    transport: number;
    food_and_misc: number;
    total: number;
}

export interface ItineraryResponse {
    trip_summary: TripSummary;
    flights: {
        airline: string;
        departure_time: string;
        arrival_time: string;
        price_eur: number;
    };
    hotels: {
        city: string;
        hotel_name: string;
        check_in: string;
        check_out: string;
        price_per_night_eur: number;
        total_price_eur: number;
    };
    daily_itinerary: DailyItinerary[];
    budget_breakdown: BudgetBreakdown;
    tips: string[];
}

// Constants for dropdowns
export const EUROPEAN_COUNTRIES = [
    { code: 'IE', name: 'Ireland' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'FR', name: 'France' },
    { code: 'DE', name: 'Germany' },
    { code: 'ES', name: 'Spain' },
    { code: 'IT', name: 'Italy' },
    { code: 'NL', name: 'Netherlands' },
    { code: 'BE', name: 'Belgium' },
    { code: 'PT', name: 'Portugal' },
    { code: 'SE', name: 'Sweden' },
    { code: 'NO', name: 'Norway' },
    { code: 'DK', name: 'Denmark' },
    { code: 'FI', name: 'Finland' },
    { code: 'AT', name: 'Austria' },
    { code: 'CH', name: 'Switzerland' }
];

export const IRISH_COUNTIES = [
    'Antrim',
    'Armagh',
    'Carlow',
    'Cavan',
    'Clare',
    'Cork',
    'Derry',
    'Donegal',
    'Down',
    'Dublin',
    'Fermanagh',
    'Galway',
    'Kerry',
    'Kildare',
    'Kilkenny',
    'Laois',
    'Leitrim',
    'Limerick',
    'Longford',
    'Louth',
    'Mayo',
    'Meath',
    'Monaghan',
    'Offaly',
    'Roscommon',
    'Sligo',
    'Tipperary',
    'Tyrone',
    'Waterford',
    'Westmeath',
    'Wexford',
    'Wicklow'
];

export const INTERESTS = [
    'History',
    'Culture',
    'Nature',
    'Food & Drink',
    'Adventure',
    'Relaxation',
    'Shopping',
    'Nightlife',
    'Family Activities',
    'Art & Museums',
    'Music',
    'Sports',
    'Architecture',
    'Photography',
    'Local Experiences'
];

export const IRISH_AIRPORTS = [
    { code: "DUB", name: "Dublin Airport" },
    { code: "ORK", name: "Cork Airport" },
    { code: "SNN", name: "Shannon Airport" },
    { code: "NOC", name: "Ireland West Airport Knock" },
    { code: "KIR", name: "Kerry Airport" }
];

export const EUROPEAN_AIRPORTS = [
    { code: "LHR", name: "London Heathrow" },
    { code: "CDG", name: "Paris Charles de Gaulle" },
    { code: "AMS", name: "Amsterdam Schiphol" },
    { code: "FRA", name: "Frankfurt Airport" },
    { code: "MAD", name: "Madrid Barajas" },
    { code: "BCN", name: "Barcelona El Prat" },
    { code: "FCO", name: "Rome Fiumicino" },
    { code: "MUC", name: "Munich Airport" },
    { code: "ZRH", name: "Zurich Airport" },
    { code: "VIE", name: "Vienna International" }
];

export const TRANSPORT_PREFERENCES = [
    "car_rental",
    "public_transport",
    "private_transfer",
    "guided_tour"
]; 