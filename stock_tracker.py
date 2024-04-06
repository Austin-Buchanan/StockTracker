# This is the Stock Tracker CLI application
import sys
import psycopg2
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
            except IndexError:
                raise SystemExit(f"Usage: {sys.argv[0]} -i <Stock_Ticker> <Stock_Price>")
        case '-s': # selects price records from the database
            if len(sys.argv) > 2:
                stockTicker = sys.argv[2]
            returnCode = select_prices(stockTicker)
        case '-c': # writes price records to a csv file
            # TO DO
            pass
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

def select_prices(stockTicker):
    sqlSelect = "SELECT * FROM stock_prices"

    if stockTicker != '':
        sqlSelect += f" WHERE stock_ticker = '{stockTicker}'"

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sqlSelect)
                rows = cur.fetchall()
                for row in rows:
                    print(row)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

if __name__ == '__main__':
    stock_tracker()