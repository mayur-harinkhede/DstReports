from supabase import create_client, Client
import time as time_module
from postgrest.exceptions import APIError
from datetime import datetime
import pytz

# Supabase credentials
SUPABASE_URL = "https://ekajhxtahcfkfcqwhgpy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVrYWpoeHRhaGNma2ZjcXdoZ3B5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3OTEwMzMsImV4cCI6MjA4NDM2NzAzM30.dfAdOAm3NB5LZuOH1g-XkiyG3ZgR7Z07fYL6D8D0ssA"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Current time of a timezone
tz_Mumbai = pytz.timezone('Asia/Kolkata')
datetime_Mumbai = datetime.now(tz_Mumbai)
time = datetime_Mumbai.strftime('%H:%M')
today = datetime_Mumbai.strftime('%Y-%m-%d')

# Convert array of dictionary ==>> array of array
def dict_list_to_2d_array(dict_list):
    if not dict_list:
        return []
    headers = list(dict_list[0].keys())
    rows = [headers] + [[row[key] for key in headers] for row in dict_list]
    return rows

# Retry function for timeout errors
def execute_with_retry(query, retries=5, delay=3):
    for attempt in range(retries):
        try:
            return query.execute()
        except APIError as e:
            if 'timeout' in str(e).lower() and attempt < retries - 1:
                print(f"Timeout on attempt {attempt+1}, retrying in {delay}s...")
                time_module.sleep(delay)
            else:
                raise

# -------- 1. SELECT MENU FIRST (To get dynamic headers) --------
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

# Safely extract menu names (with fallbacks just in case)
if rows_menu:
    dateOfDelivery = rows_menu[0]["menu_date"]
    rice_name = rows_menu[0]["rice"] if rows_menu[0]["rice"] else "Rice"
    dal_name = rows_menu[0]["dal"] if rows_menu[0]["dal"] else "Dal"
    curry_name = rows_menu[0]["curry"] if rows_menu[0]["curry"] else "Curry"
    # Chikki: only present on the days the menu table has it set for that date
    chikki_name = rows_menu[0]["chikki"] if rows_menu[0].get("chikki") else None
    curryRatio = rows_menu[0]["curry_couldron_volume"]
    DalRatio = rows_menu[0]["dal_couldron_volume"]
    riceRatio = rows_menu[0]["rice_couldron_volume"]
else:
    dateOfDelivery, rice_name, dal_name, curry_name, curryRatio = today, "Rice", "Dal", "Curry", 1
    chikki_name = None

menu = {
    "Rice": rice_name,
    "Dal": dal_name,
    "Curry": curry_name,
    "Date": dateOfDelivery
}
if chikki_name:
    menu["Chikki"] = chikki_name

print(menu)

# -------- 2. SELECT cummulative_report --------
select_response = execute_with_retry(supabase.table("cummulative_report").select("*"))
rows = select_response.data
_last = rows[-1] if rows else {}

# -------- 3. BUILD DYNAMIC HEADERS --------
needed_cols = [
    'v_combined', 'di_total_school', 'di_running_school',
    'di_ps', 'di_ups', 'di_zphs', 'di_total_attendance'
]

proper_headers_row0 = ['', '', 'Schools', '', 'Attendance', '', '', '']
proper_headers_row1 = ['Sr. No', 'Route', 'Total', 'Running', 'PS', 'UPS', 'ZPHS', 'Total']

total_rice = total_dal = total_curry = total_chikki = 0
rice_couldron = dal_couldron = curry_couldron = 0

# Check Menu and dynamically append Rice columns
if rows_menu and rows_menu[0].get("rice"):
    needed_cols.extend(['rice100', 'rice75', 'rice50', 'rice25', 'rice13', 'di_rice_vessels'])
    proper_headers_row0.extend([rice_name, '', '', '', '', ''])
    proper_headers_row1.extend(['100', '75', '50', '25', '13', 'Total'])
    total_rice = (_last.get('rice100', 0) * 22) + (_last.get('rice75', 0) * 16.5) + (_last.get('rice50', 0) * 11) + (_last.get('rice25', 0) * 5.5) + (_last.get('rice13', 0) * 2.75)
    rice_couldron = total_rice / riceRatio if riceRatio else 0

# Check Menu and dynamically append Dal columns
if rows_menu and rows_menu[0].get("dal"):
    needed_cols.extend(['dal150', 'dal100', 'dal75', 'dal50', 'dal25', 'dal13', 'di_dal_vessels'])
    proper_headers_row0.extend([dal_name, '', '', '', '', '', ''])
    proper_headers_row1.extend(['150', '100', '75', '50', '25', '13', 'Total'])
    total_dal = (_last.get('dal150', 0) * 27) + (_last.get('dal100', 0) * 18) + (_last.get('dal75', 0) * 13.50) + (_last.get('dal50', 0) * 9) + (_last.get('dal25', 0) * 4.50) + (_last.get('dal13', 0) * 2.34)
    dal_couldron = total_dal / DalRatio if DalRatio else 0

# Check Menu and dynamically append Curry columns
if rows_menu and rows_menu[0].get("curry"):
    needed_cols.extend(['curry100', 'curry75', 'curry50', 'curry25', 'curry13', 'di_curry_vessels'])
    proper_headers_row0.extend([curry_name, '', '', '', '', ''])
    proper_headers_row1.extend(['100', '75', '50', '25', '13', 'Total'])
    total_curry = (_last.get('curry100', 0) * 18) + (_last.get('curry75', 0) * 13.50) + (_last.get('curry50', 0) * 9) + (_last.get('curry25', 0) * 4.50) + (_last.get('curry13', 0) * 2.34)
    curry_couldron = total_curry / curryRatio if curryRatio else 0

# Always append Vessels
needed_cols.append('di_total_vessels')
proper_headers_row0.append('')
proper_headers_row1.append('Vessels')

# Check for Extras (Curd, Snack, Pickle)
if _last.get('di_curd_kg') and _last['di_curd_kg'] > 0:
    needed_cols.append('di_curd_kg')
    proper_headers_row0.append('')
    proper_headers_row1.append('Curd')

if _last.get('di_snack_kg') and _last['di_snack_kg'] > 0:
    needed_cols.append('di_snack_kg')
    proper_headers_row0.append('')
    proper_headers_row1.append('Snack')

if _last.get('di_pickle_kg') and _last['di_pickle_kg'] > 0:
    needed_cols.append('di_pickle_kg')
    proper_headers_row0.append('')
    proper_headers_row1.append('pickle')

# NEW: Chikki — shown only when the menu for that date includes it.
menu_has_chikki = bool(chikki_name)
if menu_has_chikki:
    needed_cols.append('di_chikki_qty')  
    proper_headers_row0.append('')
    proper_headers_row1.append('Chikki')

# ==========================================
# SNACK ROUTING LOGIC: CHANGE THIS VARIABLE
# Options: "first" (1-32), "second" (33-64), or "all"

# ==========================================
# ==========================================
# SNACK ROUTING LOGIC: ASK FOR USER INPUT
# ==========================================
print("\n--- Snack Distribution Setup ---")
print("Which routes should receive snacks today?")
print("Type 'first'  for routes 1-32")
print("Type 'second' for routes 33-65")
print("Type 'all'    for all routes")

while True:
    snack_choice = input("Enter your choice (first/second/all): ").strip().lower()
    if snack_choice in ['first', 'second', 'all']:
        break
    else:
        print("Invalid input! Please type exactly 'first', 'second', or 'all'.")

print(f"Got it! Processing snacks for: {snack_choice}...\n")
# ==========================================
# Build final result array with injected Sr. No
filtered_rows = []
actual_snack_total = 0 

for i, r in enumerate(rows):
    is_total_row = str(r.get('v_combined', '')).lower() == 'total'
    sr_val = "" if is_total_row else (i + 1)

    row_dict = {'sr_no': sr_val}
    for col in needed_cols:
        if col == 'di_chikki_qty':
            # Chikki count for this route = this route's total attendance
            row_dict[col] = r.get('di_total_attendance', 0)
        
        elif col == 'di_snack_kg':
            if is_total_row:
                # Assign the newly calculated total to the final Total row
                row_dict[col] = actual_snack_total
            else:
                snack_val = r.get(col, 0)
                route_num = i + 1
                
                # Apply the logic: first 32 or next 32
                if snack_choice == "first" and route_num > 32:
                    snack_val = 0
                elif snack_choice == "second" and route_num <= 32:
                    snack_val = 0
                    
                row_dict[col] = snack_val
                actual_snack_total += snack_val 
        
        else:
            row_dict[col] = r.get(col, 0)
            
    filtered_rows.append(row_dict)

result = dict_list_to_2d_array(filtered_rows)
result = [proper_headers_row0, proper_headers_row1] + result[1:]

# -------- 4. CALCULATE TOTALS --------
if menu_has_chikki:
    total_chikki = _last.get('di_total_attendance', 0)
else:
    total_chikki = 0

row = {
    'Rice':          total_rice,
    'RiceCouldron':  rice_couldron,
    'Dal':           total_dal,
    'DalCouldron':   dal_couldron,
    'Curry':         total_curry,
    'CurryCouldron': curry_couldron,
    'Curd':          _last.get('di_curd_kg', 0),
    'Snack':         actual_snack_total if 'di_snack_kg' in needed_cols else 0, # Uses our new total
    'pickle':        _last.get('di_pickle_kg', 0),
    'Chikki':        total_chikki,
}