 Flight Statistics Application

Flight Statistics Application
=============================

This application is a simple Flask web app that allows users to input a 3-letter airport code and displays a table showing the countries and the total number of flights originating from those countries and arriving at the specified airport. The data is fetched in real-time using the [FlightAPI.io](https://www.flightapi.io/) API.

Table of Contents
-----------------

*   [Prerequisites](#prerequisites)
*   [Installation](#installation)
*   [Usage](#usage)
    *   [API Key Setup](#api-key-setup)
    *   [Running the Application](#running-the-application)
*   [Notes](#notes)
*   [License](#license)

Prerequisites
-------------

Before you begin, ensure you have met the following requirements:

*   **Python 3.x** installed on your local machine.
*   **pip** (Python package installer) is available.
*   An API key from [FlightAPI.io](https://www.flightapi.io/). Sign up for a free account to obtain your API key.

Installation
------------

1.  **Clone the Repository**
    
        git clone https://github.com/yourusername/yourrepository.git
        cd yourrepository
        
    
2.  **Create a Virtual Environment (Optional but Recommended)**
    
        python -m venv venv
        
    
    Activate the virtual environment:
    
    *   On Windows:
        
            venv\Scripts\activate
            
        
    *   On macOS/Linux:
        
            source venv/bin/activate
            
        
3.  **Install Required Packages**
    
        pip install -r requirements.txt
        
    
    If you don't have a `requirements.txt` file, you can install the packages individually:
    
        pip install flask requests
        
    

Usage
-----

### API Key Setup

The application requires an API key from FlightAPI.io to fetch real-time flight data. Set your API key as an environment variable named `FLIGHTAPI_KEY`.

*   **On Windows:**
    
        set FLIGHTAPI_KEY=your_api_key
        
    
*   **On macOS/Linux:**
    
        export FLIGHTAPI_KEY=your_api_key
        
    

Alternatively, you can create a `.env` file in the project root directory and add the following line:

    FLIGHTAPI_KEY=your_api_key
    

Make sure to replace `your_api_key` with your actual API key.

### Running the Application

1.  **Ensure You're in the Project Directory**
    
        cd yourrepository
        
    
2.  **Set the Environment Variable (If Not Already Set)**
    
    (Refer to the [API Key Setup](#api-key-setup) section.)
    
3.  **Run the Flask Application**
    
        python app.py
        
    
4.  **Access the Application in Your Web Browser**
    
    Open your browser and navigate to `http://127.0.0.1:5000/`.
    
5.  **Use the Application**
    *   Enter a valid 3-letter airport code (e.g., `LAX`, `JFK`, `DOH`).
    *   Click the **Submit** button.
    *   View the table displaying countries and the number of flights arriving at the specified airport from each country.

Notes
-----

*   **API Limitations**
    *   The free plan of FlightAPI.io may have limitations on the number of API requests per day.
    *   Be mindful of the number of requests to avoid exceeding your quota.
*   **Error Handling**
    *   The application includes basic error handling for invalid inputs and API errors.
    *   If you encounter errors, ensure that your API key is valid and that you have internet connectivity.
*   **Virtual Environment**
    *   Using a virtual environment is recommended to avoid conflicts with other Python packages on your system.
    *   Remember to activate the virtual environment each time you work on the project.

License
-------

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.