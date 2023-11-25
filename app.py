from flask import Flask, render_template
import csv

app = Flask(__name__)

#Load stock symbols from CSV file
def load_symbols_from_csv():
    symbols = []
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) 
        for row in reader:
            symbols.append(row[0])
    return symbols

@app.route('/')
def index():
    #get stock symbols from CSV
    stock_symbols = load_symbols_from_csv()

    #get chart types
    chart_types = get_chart_types()

    #get time series
    time_series = get_time_series()

    return render_template('index.html', stock_symbols=stock_symbols, chart_types=chart_types, time_series=time_series)

def get_chart_types():
    chart_types = ['1.Line', '2.Bar']
    return chart_types

def get_time_series():
    time_series = ['1.Intraday', '2.Daily', '3.Weekly', '4.Monthly']
    return time_series


if __name__ == '__main__':
    app.run(debug=True)

