import psycopg2
from config import load_config
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/stock")
async def get_tickers():
    sqlSelect = "SELECT stock_ticker FROM stock_names;"
    tickers = []
    success = False
    success, tickers = execute_SQL(sqlSelect)
    if not success:
        return {"error": tickers[0]}
    return {"available_tickers": tickers}

@app.get("/stock/{ticker}")
async def get_recent_price(ticker: str):
    sqlSelect = """SELECT B.stock_name, A.stock_ticker, A.stock_price, A.time_priced 
                   FROM stock_prices A inner join stock_names B 
                   ON A.stock_ticker = B.stock_ticker 
                   WHERE A.stock_ticker = '{0}' 
                   ORDER BY A.time_priced DESC 
                   LIMIT 1;""".format(ticker)
    results = []
    success = False
    success, results = execute_SQL(sqlSelect)
    if not success:
        return {"error": results[0]}
    return {
       "stock_name": results[0][0],
       "stock_ticker": results[0][1],
       "stock_price": results[0][2],
       "time_priced": results[0][3] 
    }

def execute_SQL(sql: str):
    config = load_config()
    rows = []
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                if sql.startswith('SELECT'):
                    rows = cur.fetchall()
                else:
                    conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        rows.append[error]
        return False, rows
    finally:
        if len(rows) > 0:
            return True, rows
        rows.append("No data found.")
        return False, rows