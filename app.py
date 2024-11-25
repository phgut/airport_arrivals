# app.py

from flask import Flask, render_template, request
import requests
import os
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# Change the API key to your own
API_KEY = "67442352eecd43b446b83f92"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        airport_code = request.form['airport_code'].upper()
        # Validate that the airport code is 3 letters
        if len(airport_code) != 3 or not airport_code.isalpha():
            error = "Please enter a valid 3-letter airport code."
            return render_template('index.html', error=error)
        # Fetch arrival flights from the API
        date_today = datetime.today().strftime('%Y-%m-%d')
        url = f'https://api.flightapi.io/compschedule/{API_KEY}?mode=arrivals&iata={airport_code}'
        response = requests.get(url)
        if response.status_code != 200:
            error = "Error fetching data from the API."
            return render_template('index.html', error=error)
        data = response.json()[0]
        # Process the data to get the required information
        arrivals_data = data.get('airport', {}).get('pluginData', {}).get('schedule', {}).get('arrivals', {}).get('data', [])
        if not arrivals_data:
            error = "No arrival data available for this airport."
            return render_template('index.html', error=error)
        country_counts = defaultdict(int)
        for flight_info in arrivals_data:
            flight = flight_info.get('flight', {})
            # Get the origin airport's country
            origin_airport_info = flight.get('airport', {}).get('origin', {})
            position_info = origin_airport_info.get('position', {})
            country_info = position_info.get('country', {})
            country_name = country_info.get('name')
            if country_name:
                country_counts[country_name] += 1
        if not country_counts:
            error = "No country data available for the flights."
            return render_template('index.html', error=error)
        # Convert the counts to a list of tuples
        country_counts_list = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
        return render_template('results.html', airport_code=airport_code, country_counts=country_counts_list)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
