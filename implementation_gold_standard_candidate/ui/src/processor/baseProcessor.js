import axios from 'axios';

// Create a singleton notification handler
let notificationHandler = null;

export const initializeBaseProcessor = (showNotification) => {
  notificationHandler = showNotification;
};

export class BaseProcessor {
  constructor() {
    this.config = new this.Config();
  }

  Config = class {
    constructor() {
      this.backendDomain = process.env.REACT_APP_API_BASE_URL;
    }

    setBackendDomain(domain) {
      this.backendDomain = domain;
    }
  }

  initialize(backendDomain = null) {
    if (backendDomain) {
      this.config.setBackendDomain(backendDomain);
    }
  }

  async makeRequest(method, endpoint, data = null, options = {}) {
    const url = `${this.config.backendDomain}${endpoint}`;
    const authToken = localStorage.getItem('authToken');
    const headers = {
      ...options.headers,
    };

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
      const response = await axios({
        method,
        url,
        data,
        headers,
        ...options
      });
      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          error.message || 
                          'An unexpected error occurred';

      console.error(`Request failed: ${method} ${endpoint}`, error);
      
      if (notificationHandler) {
        notificationHandler({
          type: 'error',
          title: 'Error',
          message: errorMessage,
          duration: 5
        });
      }
      
      throw error;
    }
  }
}
