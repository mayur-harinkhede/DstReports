import os
import sys
import time

# --- Dynamic Path Mapping Patch (resolves Windows C:\Users\TAPF... paths to local server paths) ---
import tempfile

def _is_serverless():
    return bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

_original_join = os.path.join

def _mocked_join(*args):
    win_prefix = r"C:\Users\TAPF\Documents\DistributionFinal\DistributionFinal"
    local_project_path = os.path.abspath(os.path.dirname(__file__))
    
    new_args = []
    for arg in args:
        if isinstance(arg, str) and arg.startswith(win_prefix):
            suffix = arg[len(win_prefix):].lstrip('\\/')
            new_arg = _original_join(local_project_path, suffix)
            new_args.append(new_arg)
        else:
            new_args.append(arg)
            
    result = _original_join(*new_args)
    
    if isinstance(result, str) and result.startswith(win_prefix):
        suffix = result[len(win_prefix):].lstrip('\\/')
        result = _original_join(local_project_path, suffix)
        
    if isinstance(result, str):
        if os.name != 'nt':
            result = result.replace('\\', '/')
        else:
            result = result.replace('/', '\\')
            
        # On serverless platforms (like Vercel), redirect runtime-generated folders ('reports' and 'image') to /tmp
        if _is_serverless():
            norm = result.replace('\\', '/')
            proj_norm = local_project_path.replace('\\', '/')
            if norm == f"{proj_norm}/reports" or norm.startswith(f"{proj_norm}/reports/"):
                suffix = norm[len(f"{proj_norm}/reports"):]
                result = f"/tmp/reports{suffix}"
            elif norm == f"{proj_norm}/image" or norm.startswith(f"{proj_norm}/image/"):
                suffix = norm[len(f"{proj_norm}/image"):]
                result = f"/tmp/image{suffix}"
            
    return result

os.path.join = _mocked_join

import glob
import builtins
import threading
import importlib
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)
generation_lock = threading.Lock()

# Define the project directory
VBCD = os.path.abspath(os.path.dirname(__file__))
if VBCD not in sys.path:
    sys.path.insert(0, VBCD)

# Context manager to mock built-in input dynamically during report generation
class WebInputMock:
    def __init__(self, extra_item='1', send_group_1='n', send_group_2='n', snack_choice='all'):
        self.extra_item = str(extra_item)
        self.send_group_1 = str(send_group_1).lower().strip()
        self.send_group_2 = str(send_group_2).lower().strip()
        self.snack_choice = str(snack_choice).lower().strip()
        self.original_input = builtins.input

    def __enter__(self):
        def mocked_input(prompt=""):
            prompt_str = str(prompt).lower()
            if "extra item" in prompt_str or "select extra" in prompt_str:
                print(f"[Web Mock] Intercepted extra item prompt. Answering: {self.extra_item}")
                return self.extra_item
            elif "internal group" in prompt_str:
                print(f"[Web Mock] Intercepted internal group Telegram prompt. Answering: {self.send_group_1}")
                return self.send_group_1
            elif "delivery group" in prompt_str:
                print(f"[Web Mock] Intercepted delivery group Telegram prompt. Answering: {self.send_group_2}")
                return self.send_group_2
            elif "snack" in prompt_str or "which routes" in prompt_str or "first/second/all" in prompt_str:
                print(f"[Web Mock] Intercepted snack choice prompt. Answering: {self.snack_choice}")
                return self.snack_choice
            
            # Safe default fallback for any unexpected inputs
            print(f"[Web Mock] Intercepted prompt: '{prompt}'. Answering default: n")
            return "n"
            
        builtins.input = mocked_input
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        builtins.input = self.original_input

def clean_image_folder():
    """Clean the temporary images folder to avoid old images appearing in the loading sheet PDF."""
    image_folder = os.path.join(VBCD, "image")
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
        return
    for f in glob.glob(os.path.join(image_folder, "*")):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except Exception as e:
            print(f"[Web App] Warning: Could not remove old image file {f}: {e}")

def clean_reports_folder():
    """Delete files in the reports folder that are older than 2 hours to save space."""
    reports_folder = os.path.join(VBCD, "reports")
    if not os.path.exists(reports_folder):
        return
    now = time.time()
    for f in glob.glob(os.path.join(reports_folder, "*")):
        try:
            if os.path.isfile(f):
                if os.path.getmtime(f) < now - 7200:
                    os.remove(f)
        except Exception as e:
            print(f"[Web App] Warning: Could not remove old report file {f}: {e}")

def send_telegram_in_background(pdf_path, send_group_1, send_group_2, report_type):
    """Sends the compiled PDF to Telegram groups in a background thread to prevent blocking download."""
    group_1_chat_id = '-1002266381119'  # Distribution Internal Group
    group_2_chat_id = '-4042324815'     # Distribution Delivery Group
    
    try:
        import telebot
        bot_token = '6077494792:AAHHVmsK5vSHclA-XNRZoegj35mAvXMabHw'
        bot = telebot.TeleBot(bot_token)
        
        if send_group_1 == 'y':
            print(f"[Background Telegram] Sending {pdf_path} to Internal Group...")
            with open(pdf_path, 'rb') as f:
                bot.send_document(group_1_chat_id, f)
            print(f"[Background Telegram] Successfully sent to Internal Group.")
            
        if send_group_2 == 'y':
            print(f"[Background Telegram] Sending {pdf_path} to Delivery Group...")
            with open(pdf_path, 'rb') as f:
                bot.send_document(group_2_chat_id, f)
            print(f"[Background Telegram] Successfully sent to Delivery Group.")
    except Exception as e:
        print(f"[Background Telegram] Error sending PDF to Telegram: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate/<report_type>')
def generate_report(report_type):
    # Only allow one generation at a time to prevent file conflicts
    with generation_lock:
        # Clean up old reports to free up space
        clean_reports_folder()
        
        extra_curd = request.args.get('extra_curd', 'n')  # y/n
        extra_snack = request.args.get('extra_snack', 'n')  # y/n
        extra_pickle = request.args.get('extra_pickle', 'n')  # y/n
        extra_chikki = request.args.get('extra_chikki', 'n')  # y/n
        send_group_1 = request.args.get('send_group_1', 'n')  # y/n
        send_group_2 = request.args.get('send_group_2', 'n')  # y/n
        snack_choice = request.args.get('snack_choice', 'all')  # first/second/all
        os.environ['EXTRA_CURD'] = extra_curd
        os.environ['EXTRA_SNACK'] = extra_snack
        os.environ['EXTRA_PICKLE'] = extra_pickle
        os.environ['EXTRA_CHIKKI'] = extra_chikki
        
        # Map first selected item as extra_item for legacy compatibility
        extra_item = '1'
        if extra_pickle == 'y':
            extra_item = '2'
        elif extra_chikki == 'y':
            extra_item = '3'
            
        pdf_path = None
        try:
            with WebInputMock(extra_item=extra_item, send_group_1=send_group_1, send_group_2=send_group_2, snack_choice=snack_choice):
                if report_type == 'cumulative':
                    # Reload dependencies so they run fresh database queries
                    modules_to_reload = [
                        'modules2.seatable',
                        'modules2.iso',
                        'modules2.cummulative',
                        'modules2.telegram',
                        'cummulative'
                    ]
                    for mod_name in modules_to_reload:
                        if mod_name in sys.modules:
                            importlib.reload(sys.modules[mod_name])
                        else:
                            importlib.import_module(mod_name)
                        # Mock telegramBot to do nothing during generation to keep download instant
                        if mod_name == 'modules2.telegram':
                            sys.modules[mod_name].telegramBot = lambda x: None
                    
                    pdf_path = sys.modules['cummulative'].pdf_filename

                elif report_type == 'delivery':
                    modules_to_reload = [
                        'modules.seatable',
                        'modules.iso',
                        'modules.data_table',
                        'modules.telegram',
                        'delivery'
                    ]
                    for mod_name in modules_to_reload:
                        if mod_name in sys.modules:
                            importlib.reload(sys.modules[mod_name])
                        else:
                            importlib.import_module(mod_name)
                        # Mock telegramBot to do nothing during generation to keep download instant
                        if mod_name == 'modules.telegram':
                            sys.modules[mod_name].telegramBot = lambda x: None
                    
                    pdf_path = sys.modules['delivery'].pdf_filename

                elif report_type == 'loading':
                    # Clean up old images before generating new ones
                    clean_image_folder()
                    
                    modules_to_reload = [
                        'modules3.seatable',
                        'modules3.loading',
                        'modules3.imageToPdf',
                        'modules3.telegram',
                        'loading'
                    ]
                    for mod_name in modules_to_reload:
                        if mod_name in sys.modules:
                            importlib.reload(sys.modules[mod_name])
                        else:
                            importlib.import_module(mod_name)
                        # Mock telegramBot to do nothing during generation to keep download instant
                        if mod_name == 'modules3.telegram':
                            sys.modules[mod_name].telegramBot = lambda x: None
                    
                    pdf_path = sys.modules['loading'].output_pdf

                else:
                    return jsonify({"error": "Unknown report type"}), 400

            if pdf_path and os.path.exists(pdf_path):
                # Start background thread to send the PDF to Telegram in parallel (instant download for user!)
                if send_group_1 == 'y' or send_group_2 == 'y':
                    threading.Thread(
                        target=send_telegram_in_background,
                        args=(pdf_path, send_group_1, send_group_2, report_type),
                        daemon=True
                    ).start()

                filename = os.path.basename(pdf_path)
                return send_file(pdf_path, as_attachment=True, download_name=filename)
            else:
                return jsonify({"error": f"Report file was not found at expected path: {pdf_path}"}), 500

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--------------------------------------------------")
    print("Starting TAPF Distribution Report Server...")
    print("Access locally at: http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(debug=True, host='0.0.0.0', port=5000)
