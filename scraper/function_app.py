import azure.functions as func
import requests
from datetime import datetime
import snowflake.connector
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = func.FunctionApp()

# --- Pull credentials from App Settings (not hardcoded) ---
TOMTOM_URL = os.getenv("API")

SF_USER     = os.environ["SF_USER"]
SF_PASSWORD = os.environ["SF_PASSWORD"]
SF_ACCOUNT  = os.environ["SF_ACCOUNT"]
SF_WAREHOUSE = os.environ["SF_WAREHOUSE"]
SF_DATABASE = os.environ["SF_DATABASE"]
SF_SCHEMA   = os.environ["SF_SCHEMA"]
TABLE_NAME  = "raw_table"

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SF_USER,
        password=SF_PASSWORD,
        account=SF_ACCOUNT,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA
    )

# Runs every hour: "0 0 * * * *" = at minute 0 of every hour
@app.timer_trigger(schedule="0 0 * * * *", arg_name="myTimer", run_on_startup=True)
def fetch_and_insert(myTimer: func.TimerRequest) -> None:
    logging.info(f"[{datetime.utcnow()}] Timer triggered — fetching TomTom data...")

    try:
        # 1. Fetch from TomTom API
        response = requests.get(TOMTOM_URL)
        response.raise_for_status()
        data = response.json()

        if not data.get("routes"):
            logging.error("API returned no routes.")
            return

        summary = data["routes"][0]["summary"]

        timestamp             = datetime.utcnow().isoformat()
        length_in_meters      = summary.get("lengthInMeters", 0)
        travel_time           = summary.get("travelTimeInSeconds", 0)
        traffic_delay         = summary.get("trafficDelayInSeconds", 0)
        traffic_length        = summary.get("trafficLengthInMeters", 0)
        departure_time        = summary.get("departureTime")
        arrival_time          = summary.get("arrivalTime")

       # 2. Insert into Snowflake
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                timestamp                TIMESTAMP_NTZ,
                length_in_meters         NUMBER,
                travel_time_in_seconds   NUMBER,
                traffic_delay_in_seconds NUMBER,
                traffic_length_in_meters NUMBER,
                departure_time           TIMESTAMP_TZ,
                arrival_time             TIMESTAMP_TZ
            )
        """)
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (timestamp, length_in_meters, travel_time, traffic_delay,
              traffic_length, departure_time, arrival_time))

        conn.commit()  # ← THIS WAS MISSING

        logging.info(f"Inserted — travel time: {travel_time}s, delay: {traffic_delay}s")
        cursor.close()
        conn.close()

    except requests.exceptions.RequestException as e:
        logging.error(f"API error: {e}")
    except snowflake.connector.errors.ProgrammingError as e:
        logging.error(f"Snowflake error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")