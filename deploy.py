import os
import sys
import time
import requests

# Set working directory to the script's directory
VBCD = r"C:\Users\TAPF\Documents\DistributionFinal\DistributionFinal"
os.chdir(VBCD)

print("==================================================")
print("     TAPF PythonAnywhere Automated Deployer       ")
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

# Define what to exclude from upload
EXCLUDE_DIRS = {'venv', 'myenv', '.git', '__pycache__', 'reports'}
EXCLUDE_FILES = {'deploy.py', 'test_app.py', 'deploy_new.py'}

# Base API url
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{username}"

def upload_file(local_path, remote_path):
    url = f"{API_BASE}/files/path{remote_path}"
    retries = 3
    for attempt in range(retries):
        print(f"Uploading: {local_path} -> {remote_path} (Attempt {attempt+1})...", end="", flush=True)
        try:
            with open(local_path, 'rb') as f:
                files = {'content': f}
                response = requests.post(url, headers=headers, files=files)
            
            if response.status_code in [200, 201]:
                print(" SUCCESS!")
                time.sleep(0.5)  # Avoid hitting rate limits
                return True
            elif response.status_code == 429:
                print(" THROTTLED. Waiting 10s...")
                time.sleep(10)
            else:
                print(f" FAILED (Status: {response.status_code})")
                print(response.text)
                return False
        except Exception as e:
            print(f" ERROR: {e}")
            time.sleep(2)
    return False

# 1. Gather all files to upload
files_to_upload = []
for root, dirs, files in os.walk('.'):
    # Skip excluded directories
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    
    for file in files:
        if file in EXCLUDE_FILES:
            continue
        # Avoid uploading generated reports or temp files in image folder
        rel_dir = os.path.relpath(root, '.')
        if rel_dir.startswith('image') and file != 'placeholder': # Skip generated images
            continue
            
        local_path = os.path.join(root, file)
        # Convert local windows path to standard unix path for PythonAnywhere
        clean_rel_path = local_path.replace('\\', '/')
        if clean_rel_path.startswith('./'):
            clean_rel_path = clean_rel_path[2:]
            
        remote_path = f"/home/{username}/DistributionFinal/{clean_rel_path}"
        files_to_upload.append((local_path, remote_path))

print(f"\nFound {len(files_to_upload)} files to deploy.")
confirm = input("Do you want to proceed with uploading? (y/n): ").strip().lower()
if confirm != 'y':
    print("Deployment cancelled.")
    sys.exit(0)

# 2. Upload files
for local, remote in files_to_upload:
    upload_file(local, remote)

# 3. Write WSGI configuration file with auto-install feature
print("\nConfiguring WSGI file...")
wsgi_content = f"""import sys
import os

# Add your project directory to the sys.path
project_home = '/home/{username}/DistributionFinal'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Auto-install missing packages
try:
    import supabase
    import reportlab
    import seatable_api
except ImportError:
    import subprocess
    print("Missing packages. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "flask", "reportlab", "supabase", "pillow", "pyTelegramBotAPI", "seatable-api", "pytz"])

# Import and run your Flask app as 'application' for PythonAnywhere
from app import app as application
"""

wsgi_remote_path = f"/var/www/{username}_pythonanywhere_com_wsgi.py"
wsgi_url = f"{API_BASE}/files/path{wsgi_remote_path}"
for attempt in range(3):
    try:
        response = requests.post(wsgi_url, headers=headers, files={'content': ('wsgi.py', wsgi_content)})
        if response.status_code in [200, 201]:
            print("WSGI File configured successfully!")
            break
        elif response.status_code == 429:
            print("WSGI config throttled. Waiting 10s...")
            time.sleep(10)
        else:
            print(f"Failed to configure WSGI File (Status: {response.status_code})")
            print(response.text)
            break
    except Exception as e:
        print(f"Error configuring WSGI: {e}")
        time.sleep(2)

# 4. Check if Web App exists, if not create it
print("\nChecking Web App setup...")
webapps_url = f"{API_BASE}/webapps/"
try:
    response = requests.get(webapps_url, headers=headers)
    webapps = response.json()
    domain = f"{username}.pythonanywhere.com"
    
    webapp_exists = False
    for app in webapps:
        if app.get('domain_name') == domain:
            webapp_exists = True
            break
            
    if not webapp_exists:
        print(f"Web App for {domain} not found. Creating a new one...")
        create_payload = {
            "domain_name": domain,
            "python_version": "python310"
        }
        create_response = requests.post(webapps_url, headers=headers, data=create_payload)
        if create_response.status_code == 201:
            print("Web App created successfully!")
        else:
            print(f"Failed to create Web App: {create_response.text}")
    else:
        print(f"Web App for {domain} already exists.")
        
    # 5. Reload Web App
    print("Reloading Web App...")
    reload_url = f"{API_BASE}/webapps/{domain}/reload/"
    reload_response = requests.post(reload_url, headers=headers)
    if reload_response.status_code == 200:
        print("\n==================================================")
        print("          DEPLOYMENT COMPLETE SUCCESSFULLY!        ")
        print(f" Visit your site at: http://{domain}")
        print("==================================================")
    else:
        print(f"Failed to reload Web App (Status: {reload_response.status_code})")
        print(reload_response.text)
except Exception as e:
    print(f"Error handling Web App setup: {e}")
