# This is the Stock Tracker CLI application
import sys
import psycopg2
from config import load_config

def stock_tracker():
    stockTicker = ''
    stockPrice = ''

    try:
        stockTicker = sys.argv[1]
        stockPrice = sys.argv[2]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <Stock_Ticker> <Stock_Price>")
    
    sqlInsert = """INSERT INTO stock_prices ("stock_ticker", "stock_price", "time_priced") VALUES ('{0}', '{1}', CURRENT_TIMESTAMP) RETURNING price_id;""".format(stockTicker, stockPrice)
    price_id = None
    config = load_config()

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
        print(price_id)

if __name__ == '__main__':
    stock_tracker()