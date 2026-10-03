import sys
import os

# Insert project path
VBCD = r"C:\Users\TAPF\Documents\DistributionFinal\DistributionFinal"
if VBCD not in sys.path:
    sys.path.insert(0, VBCD)

from app import app

# Create a test client
client = app.test_client()

print("Testing Cumulative Report Generation:")
response = client.get('/generate/cumulative?send_group_1=n&send_group_2=n')
print(f"Status Code: {response.status_code}")
try:
    print(response.get_json())
except Exception:
    print(response.data[:500])

print("\nTesting Delivery Report Generation:")
response = client.get('/generate/delivery?extra_curd=n&extra_snack=n&extra_pickle=n&extra_chikki=y&send_group_1=n&send_group_2=n')
print(f"Status Code: {response.status_code}")
try:
    print(response.get_json())
except Exception:
    print(response.data[:500])

print("\nTesting Loading Report Generation:")
response = client.get('/generate/loading?send_group_1=n&send_group_2=n')
print(f"Status Code: {response.status_code}")
try:
    print(response.get_json())
except Exception:
    print(response.data[:500])
