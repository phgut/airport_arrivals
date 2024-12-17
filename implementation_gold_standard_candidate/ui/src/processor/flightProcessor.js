import { BaseProcessor } from './baseProcessor';

class FlightProcessor extends BaseProcessor {
  constructor() {
    super();
    this.baseEndpoint = `${process.env.REACT_APP_FLIGHT_ENDPOINT}`; // Adjust the endpoint as needed
  }

  async getFlightsByCountry(searchTerm = '') {
    try {
      const response = await this.makeRequest(
        'get', 
        `${this.baseEndpoint}/search?term=${encodeURIComponent(searchTerm)}`
      );
      return response;
    } catch (error) {
      console.error('Error fetching flights:', error);
      throw error;
    }
  }
}

export const flightProcessor = new FlightProcessor();