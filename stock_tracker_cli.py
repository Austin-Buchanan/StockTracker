# This is the Stock Tracker CLI application
import sys
import psycopg2
import csv
import os
from config import load_config

def stock_tracker():
    option = ''
    try:
        option = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} -<Option> [<Stock_Ticker>] [<Stock_Price>]")

    returnCode = None
    stockTicker = ''
    match option:
        case '-i': # inserts a stock price to the database
            stockPrice = ''
            try:
                stockTicker = sys.argv[2]
                stockPrice = sys.argv[3]
                returnCode = add_price(stockTicker, stockPrice)
                stockName = get_name(stockTicker)
                if stockName is None:
                    nameInput = input("This ticker is not associated with a name in the database. Please enter a name for it: ")
                    add_name(stockTicker, nameInput)
            except IndexError:
                raise SystemExit(f"Usage: {sys.argv[0]} -i <Stock_Ticker> <Stock_Price>")
        case '-s': # selects price records from the database
            if len(sys.argv) > 2:
                stockTicker = sys.argv[2]
            rows = select_prices(stockTicker)
            for row in rows:
                print(row)
        case '-c': # writes price records to a csv file
            if len(sys.argv) > 2:
                stockTicker = sys.argv[2]
            returnCode = write_csv(stockTicker)
        case '-n': # gets the name of a stock ticker
            try:
                stockTicker = sys.argv[2]
                name = get_name(stockTicker)
                print(name)
            except IndexError:
                raise SystemExit(f"Usage: {sys.argv[0]} -n <Stock_Ticker>") 
        case _:
            print("Unknown option.")

    if returnCode is not None:
        print('Operation successful.')    

def add_price(stockTicker, stockPrice):
    sqlInsert = """INSERT INTO stock_prices ("stock_ticker", "stock_price", "time_priced") VALUES ('{0}', '{1}', CURRENT_TIMESTAMP) RETURNING price_id;""".format(stockTicker, stockPrice)
    config = load_config()
    price_id = None
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sqlInsert)
                rows = cur.fetchone()
                if rows:
                    price_id = rows[0]
                conn.commit()        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return price_id
    
def add_name(stockTicker: str, stockName: str):
    sqlInsert = """INSERT INTO stock_names ("stock_ticker", "stock_name") VALUES ('{0}', '{1}') RETURNING stock_ticker;""".format(stockTicker, stockName)
    config = load_config()
    try: 
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sqlInsert)
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def select_prices(stockTicker):
    sqlSelect = "SELECT stock_ticker, stock_price, time_priced FROM stock_prices"

    if stockTicker != '':
        sqlSelect += f" WHERE stock_ticker = '{stockTicker}'"

    config = load_config()
    rows = []
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sqlSelect)
                rows = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return rows

def write_csv(stockTicker):
    rows = select_prices(stockTicker)
    with open('./Output/stock_prices.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Stock Ticker', 'Price', 'Time'])
        for row in rows:
            writer.writerow([row[0], row[1], row[2]])
    return os.path.getsize('./Output/stock_prices.csv')

def get_name(stockTicker):
    sqlSelect = f"SELECT stock_name FROM stock_names WHERE stock_ticker = '{stockTicker}';"
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sqlSelect)
                row = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    if row is None:
        return None
    return row[0]

if __name__ == '__main__':
    stock_tracker()