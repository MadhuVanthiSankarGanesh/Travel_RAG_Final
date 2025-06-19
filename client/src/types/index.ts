export interface TravelData {
  origin: string;
  destination: string;
  departureDate: Date | undefined;
  returnDate: Date | undefined;
  adults: number;
  children: number[];
  travelClass: string;
  location: string;
  checkIn: Date | undefined;
  checkOut: Date | undefined;
  roomQty: number;
  currencyCode: string;
  languageCode: string;
  locationCode: string;
  stops: string;
  sort: string;
  selectedInterests: string[];
}

export interface Location {
  value: string;
  label: string;
}

export interface Interest {
  value: string;
  label: string;
} 