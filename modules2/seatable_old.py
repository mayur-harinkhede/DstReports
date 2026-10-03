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



rowsDate= base.query(f"select  *from Menu where Date > '{today}' and holidaydetails is not null Limit 1")
dateOfDelivery= rowsDate[0]["Date"]

Menu={
        "Rice":rowsDate[0]["Rice"],
        "Dal" :rowsDate[0]["Dal"],
        "Curry" :rowsDate[0]["Curry"]
        }

curryRatio=1
if "Sweet" in rowsDate[0]["Curry"]:
   print("Sweet") 
   curryRatio=1/3;
  

def dict_list_to_2d_array(dict_list):
    if not dict_list:
        return []

    headers = list(dict_list[0].keys())
    rows = [headers] + [[row[key] for key in headers] for row in dict_list]
    return rows

sql=f"""select RouteSql as Route, sum(`TotalSchool`) AS `Total Schools`, sum(`RunningSchool`) AS `Running Schools`,
    sum(`PS`) AS PS, sum(`UPS`) AS UPS, sum(`ZPHS`) AS ZPHS, sum(`TotalAttendance`) AS Total, 
    sum(`Rice 100%`) AS R100, sum(`Rice 75%`) AS R75, sum(`Rice 50%`) AS R50, sum(`Rice 25%`) AS R25, sum(`Rice 13%`) AS R13, sum(`RiceVessels`) AS Rice, 
    sum(`Dal 150%`) AS D150,sum(`Dal 100%`) AS D100, sum(`Dal 75%`) AS D75, sum(`Dal 50%`) AS D50, sum(`Dal 25%`) AS D25, sum(`Dal 13%`) AS D13, sum(`DalVessels`) AS Dal, 
    sum(`Curry 100%`) AS C100, sum(`Curry 75%`) AS C75, sum(`Curry 50%`) AS C50, sum(`Curry 25%`) AS C25, sum(`Curry 13%`) AS C13 ,sum(`CurryVessels`) AS Curry,
    sum(`Total Vessels`) AS Vessels, sum(`CurdKg`) AS Curd, sum(`SnacksFinal`) AS Snack
    from `Daily Indent` WHERE DOD="{dateOfDelivery}" group by RouteSql  ORDER BY RouteSql"""



rows= base.query(sql)
result = dict_list_to_2d_array(rows)
print(len(rows))

if curryRatio==1:
      print("Curry Ration is 01")
      sql=f"select DOD, sum(rice_kg) as Rice, sum(CurdKg) as Curd, sum(SnackKg) as Snack, sum(DalKg) as Dal, sum(CurryKg) as Curry, sum(RiceCouldron) as RiceCouldron, sum(DalCouldron) as DalCouldron, sum(CurryCouldron) as CurryCouldron from `Daily Indent` WHERE DOD='{dateOfDelivery}' group by DOD"
else:
     print("Curry Ration is not 01")
     sql=f"select DOD, sum(RiceKg) as Rice, sum(CurdKg) as Curd, sum(SnackKg) as Snack, sum(DalKg) as Dal, sum(SweetKg) as Curry, sum(RiceCouldron) as RiceCouldron, sum(DalCouldron) as DalCouldron, sum(SweetCouldron) as CurryCouldron from `Daily Indent` WHERE DOD='{dateOfDelivery}' group by DOD"

curryRatio=1
#Get summary by grouping by DOD
rows= base.query(sql)
row=rows[0]




Data=result
# Chat GPT Code summation of Arrray of Array and Add total at last:
data=[]        
for item in Data[1:]:
    data.append(item[1:])

# Transpose and sum each column
vertical_total = [sum(x for x in col if x is not None) for col in zip(*data)]


# Append totals as the last row
Data.append(["Total"]+vertical_total)

result=Data
#print(result[0])

#Changing titles now in array format since in dictionary we cant change it:
#Len 28, Title:['Route', 'Total Schools', 'Running Schools', 'PS', 'UPS', 'ZPHS', 'Total', 'R100', 'R75', 'R50', 'R25', 'R13', 'Rice', 'D150', 'D100', 'D75', 'D50', 'D25', 'D13', 'Dal', 'C100', 'C75', 'C50', 'C25', 'C13', 'Curry', 'Curd', 'Snack']
Title=['Route', 'Total', 'Running', 'PS', 'UPS', 'ZPHS', 'Total', '100', '75', '50', '25', '13', 'Total', '150', '100', '75', '50', '25', '13', 'Total', '100', '75', '50', '25', '13', 'Total',"Vessels" ,'Curd', 'Snack']
result[0]=Title


# Super top title plannning with this trick:
array = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "20", "21", "22", "23", "24", "25", "26", "27"
]

array[1]="Schools"
array[3] ="Attendance"
array[7] =rowsDate[0]["Rice"]
array[13] =rowsDate[0]["Dal"]
array[20] =rowsDate[0]["Curry"]

array[0] =""
array[26] =""
array[27] =""


result=[array]+result


