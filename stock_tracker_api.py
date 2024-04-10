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
        return True, rows