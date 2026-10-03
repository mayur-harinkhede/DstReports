from supabase import create_client, Client
import os
import sys

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

# Parse chosen items based on environment variables (Flask mode) or fallback to input (CLI mode)
extra_curd = os.environ.get('EXTRA_CURD')
extra_snack = os.environ.get('EXTRA_SNACK')
extra_pickle = os.environ.get('EXTRA_PICKLE')
extra_chikki = os.environ.get('EXTRA_CHIKKI')

if extra_snack is not None:
    # Flask mode: Parse multi-select items
    selected_items = []
    
    if extra_curd == 'y':
        selected_items.append(("Curd", "delivery_report_snack", "di_curd_kg"))
    if extra_snack == 'y':
        selected_items.append(("Snack", "delivery_report_snack", "di_snack_kg"))
    if extra_pickle == 'y':
        selected_items.append(("Pickle", "delivery_report_pickle", "di_pickle_kg"))
    if extra_chikki == 'y':
        selected_items.append(("Chikki", "delivery_report_chikki", "chikki"))
else:
    # CLI mode: fallback to single select input prompt
    extra_item_index = int(input("Select extra item number: 1. Curd, 2. Snack, 3. Pickle, 4. Chikki: "))
    extra_item_index = extra_item_index - 1
    extra_item_array = [
        ("Curd", "delivery_report_snack", "di_curd_kg"),
        ("Snack", "delivery_report_snack", "di_snack_kg"),
        ("Pickle", "delivery_report_pickle", "di_pickle_kg"),
        ("Chikki", "delivery_report_chikki", "chikki")
    ]
    selected_items = [extra_item_array[extra_item_index]]

# -------- SELECT --------
# Always load base rows from delivery_report_snack as it contains all base school details and columns up to Curry
select_response = supabase.table("delivery_report_snack").select("*").order("route").order("di_school_sr").execute()
rows = select_response.data

# Merge selected items columns from other views conditionally
has_pickle = any(item[0] == "Pickle" for item in selected_items)
has_chikki = any(item[0] == "Chikki" for item in selected_items)

if has_pickle:
    extra_rows = supabase.table("delivery_report_pickle").select("di_school_sr", "route", "di_pickle_kg").order("route").order("di_school_sr").execute().data
    for idx, r in enumerate(rows):
        r["di_pickle_kg"] = extra_rows[idx]["di_pickle_kg"] if idx < len(extra_rows) else 0

if has_chikki:
    extra_rows = supabase.table("delivery_report_chikki").select("di_school_sr", "route", "chikki").order("route").order("di_school_sr").execute().data
    for idx, r in enumerate(rows):
        r["chikki"] = extra_rows[idx]["chikki"] if idx < len(extra_rows) else 0

# Query the menu table
select_response_menu = (
    supabase.table("menu")
    .select("*")
    .gt("menu_date", f"{today}")
    .or_("holiday_details.is.null,holiday_details.eq.")
    .order("menu_date")
    .limit(1)
    .execute()
)
rows_menu = select_response_menu.data

dateOfDelivery = rows_menu[0]["menu_date"]
rice = rows_menu[0]["rice"]
dal = rows_menu[0]["dal"]
curry = rows_menu[0]["curry"]
menu = [rice, dal, curry, dateOfDelivery]
print(menu)

# Base column keys up to Curry (excluding Curd):
desired_keys = [
    'di_school_sr', 'di_school_name', 'di_eps', 'di_eups', 'di_ezphs', 'di_e_total_attendance',
    'di_ps', 'di_ups', 'di_zphs', 'di_total_attendance',
    'di_rice_100', 'di_rice_75', 'di_rice_50', 'di_rice_25', 'di_rice_13', 'di_rice_vessels',
    'di_dal_150', 'di_dal_100', 'di_dal_75', 'di_dal_50', 'di_dal_25', 'di_dal_13', 'di_dal_vessels',
    'di_curry_100', 'di_curry_75', 'di_curry_50', 'di_curry_25', 'di_curry_13', 'di_curry_vessels'
]

# Append keys of all selected extra items
for name, view_name, col_key in selected_items:
    desired_keys.append(col_key)

# Append trailing keys
desired_keys.extend(['Time', 'Singnature', 'route'])

# Convert to 2D array with guaranteed column ordering
result = [desired_keys] + [[row.get(key, 0) if row.get(key) is not None else 0 for key in desired_keys] for row in rows]

# Creating new array of unique routes for each route delivery reports:
routeArray = []
for row in rows:
    if row["route"] not in routeArray:
        routeArray.append(row["route"])

# Set headers row TitleArray dynamically in seatable so it matches the data columns count
# (This will be overwritten by TitleArray inside data_table anyway, but we keep it here for clarity)
extra_item_names = [item[0] for item in selected_items]
extra_item_name = " & ".join(extra_item_names)

# Dynamic Menu Check: If Curry is not served, zero out the third item columns (23 to 28)
is_curry_empty = (not curry) or (str(curry).strip() == "")
if is_curry_empty:
    for r_idx in range(1, len(result)):
        for c_idx in [23, 24, 25, 26, 27, 28]:
            if c_idx < len(result[r_idx]):
                result[r_idx][c_idx] = 0
