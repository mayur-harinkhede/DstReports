from seatable_api import Base, context
server_url = context.server_url or 'https://cloud.seatable.io'
api_token = context.api_token or '37398967ccfa7a6acfc92e8224efa324b99310c3'
base = Base(api_token, server_url)
base.auth()

    
# Current time of a timezone
from datetime import datetime
import pytz
tz_Mumbai = pytz.timezone('Asia/Kolkata')
datetime_Mumbai = datetime.now(tz_Mumbai)
time=datetime_Mumbai.strftime('%H:%M')
today= datetime_Mumbai.strftime('%Y-%m-%d')

rowsDate= base.query(f"select  *from Menu where Date > '{today}' Limit 1")
dateOfDelivery= rowsDate[0]["Date"]


def dict_list_to_2d_array(dict_list):
    if not dict_list:
        return []

    headers = list(dict_list[0].keys())
    rows = [headers] + [[row[key] for key in headers] for row in dict_list]
    return rows


sql=f"""select Route, 
    sum(`Rice 100%`) AS R100, sum(`Rice 75%`) AS R75, sum(`Rice 50%`) AS R50, sum(`Rice 25%`) AS R25, sum(`Rice 13%`) AS R13, sum(`RiceVessels`) AS Rice, 
    sum(`Dal 150%`) AS D150,sum(`Dal 100%`) AS D100, sum(`Dal 75%`) AS D75, sum(`Dal 50%`) AS D50, sum(`Dal 25%`) AS D25, sum(`Dal 13%`) AS D13, sum(`DalVessels`) AS Dal, 
    sum(`Curry 100%`) AS C100, sum(`Curry 75%`) AS C75, sum(`Curry 50%`) AS C50, sum(`Curry 25%`) AS C25, sum(`Curry 13%`) AS C13 ,sum(`CurryVessels`) AS Curry,
    AVG(ExpectTime) AS Time
    from `Daily Indent` WHERE DOD="{dateOfDelivery}" group by Route ORDER BY Route"""


rows= base.query(sql)
results = dict_list_to_2d_array(rows)
print("Routes: "+str(len(rows)))


#print(seconds_to_h_mm(rows[0]["Time"]))