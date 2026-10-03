from supabase import create_client, Client
import time as time_module
from postgrest.exceptions import APIError

# Supabase credentials
SUPABASE_URL = "https://ekajhxtahcfkfcqwhgpy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrYWpoeHRhaGNma2ZjcXdoZ3B5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3OTEwMzMsImV4cCI6MjA4NDM2NzAzM30.dfAdOAm3NB5LZuOH1g-XkiyG3ZgR7Z07fYL6D8D0ssA"
# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Current time of a timezone
from datetime import datetime
import pytz
tz_Mumbai = pytz.timezone('Asia/Kolkata')
datetime_Mumbai = datetime.now(tz_Mumbai)
time = datetime_Mumbai.strftime('%H:%M')
today = datetime_Mumbai.strftime('%Y-%m-%d')

# ChatGpt function to convert array of dictionary ==>> array of array:
def dict_list_to_2d_array(dict_list):
    if not dict_list:
        return []

    headers = list(dict_list[0].keys())
    rows = [headers] + [[row[key] for key in headers] for row in dict_list]
    return rows

# Retry function for intermittent timeout errors
def execute_with_retry(query, retries=5, delay=2):
    for attempt in range(retries):
        try:
            return query.execute()
        except APIError as e:
            if 'timeout' in str(e).lower() and attempt < retries - 1:
                print(f"Timeout on attempt {attempt+1}, retrying in {delay}s...")
                time_module.sleep(delay)
            else:
                raise

# -------- SELECT --------
select_response = execute_with_retry(supabase.table("loading_report").select("*"))
rows = select_response.data

select_response_menu = execute_with_retry(
    supabase.table("menu")
    .select("*")
    .gt("menu_date", f"{today}")
    .or_("holiday_details.is.null,holiday_details.eq.")
    .order("menu_date")
    .limit(1)
)

rows_menu = select_response_menu.data

dateOfDelivery = rows_menu[0]["menu_date"]
rice = rows_menu[0]["rice"]
dal = rows_menu[0]["dal"]
curry = rows_menu[0]["curry"]
menu = [rice, dal, curry, dateOfDelivery]
print(menu)

results = dict_list_to_2d_array(rows)

# Dynamic Menu Check: If Curry is not served, zero out the third item columns (14 to 19)
is_curry_empty = (not curry) or (str(curry).strip() == "")
if is_curry_empty:
    for r_idx in range(1, len(results)):
        for c_idx in [14, 15, 16, 17, 18, 19]:
            if c_idx < len(results[r_idx]):
                results[r_idx][c_idx] = 0
