from flask import Flask, render_template, request, flash, redirect, url_for
import csv
import requests
import json
import pygal
from datetime import datetime
import secrets 

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
api_key = '3EOBLEIFFPM5I97S'

#Load stock symbols from CSV file
def load_symbols_from_csv():
    symbols = []
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) 
        for row in reader:
            symbols.append(row[0])
    return symbols

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form.get('symbols')
        chart_type = request.form.get('charts')
        selected_time_series = request.form.get('timeseries')
        start_date = request.form.get('startdate')
        end_date = request.form.get('enddate')

        # Error checking
        if not start_date or not end_date:
            flash('Both start date and end date are required.')
        elif datetime.strptime(end_date, '%Y-%m-%d') < datetime.strptime(start_date, '%Y-%m-%d'):
            flash('End date cannot be earlier than start date.')
        else:
            time_series_keys = get_time_series()
            #print("Selected time series:", selected_time_series)
            #print("Available time series keys:", time_series_keys)

            #Handle the case when the selected time series is not found
            if selected_time_series not in time_series_keys:
                return "Invalid time series selected." #I got this printed because I ran out of api calls per day

            time_series = time_series_keys[selected_time_series]
            
            stock_data = retrieve_data(time_series, symbol, api_key, start_date, end_date)

            if stock_data and f'Time Series ({time_series})' in stock_data:
                #print(f"Time series key: f'Time Series ({time_series})'")
                #print("Keys in stock_data:", stock_data.keys())
                if chart_type == chart_types[0]:
                    dates, open_prices, high_prices, low_prices, close_prices = extract_chart_data(stock_data[f'Time Series ({time_series})'])
                    # Create Pygal line chart
                    line_chart = create_line_chart(symbol, time_series, dates, open_prices, high_prices, low_prices, close_prices)
                    # Render the chart
                    chart_content = line_chart.render()

                elif chart_type == chart_types[1]:
                    dates, open_prices, high_prices, low_prices, close_prices = extract_chart_data(stock_data[f'Time Series ({time_series})'])
                    # Create Pygal bar chart
                    bar_chart = create_bar_chart(symbol, time_series, dates, open_prices, high_prices, low_prices, close_prices)
                    # Render the chart
                    chart_content = bar_chart.render()
                else:
                    return "Invalid chart type selected."
                
                return render_template('index.html', chart_content=chart_content)
            else:
                return f"Error retrieving {time_series} stock data"

    # get stock symbols from CSV
    stock_symbols = load_symbols_from_csv()
    # get chart types
    chart_types = get_chart_types()
    time_series_keys = get_time_series()
    return render_template('index.html', stock_symbols=stock_symbols, chart_types=chart_types, time_series_keys=time_series_keys)

def print_pretty(data: dict):
  print(json.dumps(data, indent=4))

def retrieve_data(function: str, symbol: str, api_key: str, start_date: str, end_date: str) -> dict:
  # query from API
  url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={api_key}'

  if start_date and end_date:
        url += f'&startDate={start_date}&endDate={end_date}'

  print("API URL:", url)  #Add this line to print the API URL

  response = requests.get(url)
  if response.status_code == 200:
    data = response.text
    parsed = json.loads(data)
    return parsed
  else:
        #Print error message when API request fails
        print(f"Error retrieving data. Status code: {response.status_code}")
        print("Response content:", response.text)  #Add this line to print the response content

def get_chart_types():
     chart_types = ['1.Line', '2.Bar']
     return chart_types

def get_time_series():
    time_series_keys = {
        '1.Intraday': 'TIME_SERIES_INTRADAY',
        '2.Daily': 'TIME_SERIES_DAILY',
        '3.Weekly': 'TIME_SERIES_WEEKLY',
        '4.Monthly': 'TIME_SERIES_MONTHLY'
    }
    return time_series_keys

#this method extract data from api into time_series (d,w,m), num_points (range dates)
def extract_chart_data(time_series: dict, num_points: int = 10) -> tuple:
     dates = list(time_series.keys())[:num_points]
     dates.reverse()
     open_prices = [float(time_series[date]['1. open']) for date in dates]
     high_prices = [float(time_series[date]['2. high']) for date in dates]
     low_prices = [float(time_series[date]['3. low']) for date in dates]
     close_prices = [float(time_series[date]['4. close']) for date in dates]
     return dates, open_prices, high_prices, low_prices, close_prices
#This method create a line chart
def create_line_chart(symbol, timeframe, dates, open_prices, high_prices, low_prices, close_prices):
     line_chart = pygal.Line()
     line_chart.title = f"Stock Data for {symbol} - {timeframe}"
     line_chart.x_labels = dates
     line_chart.add('Open', open_prices)
     line_chart.add('High', high_prices)
     line_chart.add('Low', low_prices)
     line_chart.add('Close', close_prices)
     return line_chart
#This method create a bar chart
def create_bar_chart(symbol, timeframe, dates, open_prices, high_prices, low_prices, close_prices):
     bar_chart = pygal.Bar()
     bar_chart.title = f"Stock Data for {symbol} - {timeframe}"
     bar_chart.x_labels = dates
     bar_chart.add('Open', open_prices)
     bar_chart.add('High', high_prices)
     bar_chart.add('Low', low_prices)
     bar_chart.add('Close', close_prices)
     return bar_chart

if __name__ == '__main__':
    app.run(debug=True)

