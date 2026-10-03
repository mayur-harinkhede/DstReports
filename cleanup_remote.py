import os
import sys
import requests

print("==================================================")
print("     TAPF PythonAnywhere Remote Storage Cleaner   ")
print("==================================================")

username = input("Enter your PythonAnywhere Username [techzone]: ").strip()
if not username:
    username = "techzone"
token = input("Enter your PythonAnywhere API Token: ").strip()

if not username or not token:
    print("Error: Username and API Token are required!")
    sys.exit(1)

headers = {
    'Authorization': f'Token {token}'
}

API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{username}"

def clean_folder_remote(folder_path):
    print(f"\nScanning remote directory: {folder_path}...")
    url = f"{API_BASE}/files/path{folder_path}"
    
    # 1. Get list of files in directory
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to scan directory (Status: {response.status_code})")
            print(response.text)
            return
        
        # PythonAnywhere directory list API returns a dict of files/subdirs
        data = response.json()
        # The structure is usually a dictionary of paths, or list. Let's handle both.
        filenames = []
        if isinstance(data, dict):
            # Often it's a dict where keys/keys of some subfield are files
            # PythonAnywhere API usually returns list of filenames directly or key 'contents' if a dir
            filenames = data.get('contents', [])
            if not filenames and isinstance(data, dict):
                # Fallback if structure is different
                filenames = list(data.keys())
        elif isinstance(data, list):
            filenames = data
            
        print(f"Found {len(filenames)} items in folder.")
        
        deleted_count = 0
        for item in filenames:
            # item is usually the full remote path (e.g. '/home/username/DistributionFinal/reports/file.pdf')
            # Check if it's a file (we don't want to delete folders, just files)
            # Typically pythonanywhere API items are paths, if it's a path let's get the filename
            clean_item_path = item
            if not clean_item_path.startswith('/'):
                clean_item_path = f"{folder_path}/{item}"
                
            # Skip placeholders if any
            if clean_item_path.endswith('/') or 'placeholder' in clean_item_path:
                continue
                
            print(f"Deleting remote file: {clean_item_path}...", end="")
            del_url = f"{API_BASE}/files/path{clean_item_path}"
            del_res = requests.delete(del_url, headers=headers)
            if del_res.status_code in [200, 204]:
                print(" SUCCESS!")
                deleted_count += 1
            else:
                print(f" FAILED (Status: {del_res.status_code})")
                
        print(f"Successfully deleted {deleted_count} files from {folder_path}.")
    except Exception as e:
        print(f"Error cleaning {folder_path}: {e}")

# Clean reports and image folders
clean_folder_remote(f"/home/{username}/DistributionFinal/reports")
clean_folder_remote(f"/home/{username}/DistributionFinal/image")

print("\n==================================================")
print("Remote storage cleanup complete! You can now run deploy.py")
print("==================================================")
