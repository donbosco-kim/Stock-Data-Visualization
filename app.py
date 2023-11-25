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
    #Get stock symbols from CSV
    stock_symbols = load_symbols_from_csv()

    return render_template('index.html', stock_symbols=stock_symbols)

if __name__ == '__main__':
    app.run(debug=True)

