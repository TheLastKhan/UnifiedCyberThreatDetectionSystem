"""
Dashboard başlatma scripti
"""

import os
import sys
import subprocess
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    """Flask dashboard'u başlatır"""
    print("Starting Unified Threat Detection Dashboard...")
    
    # Change to web_dashboard directory
    dashboard_dir = "web_dashboard"
    if not os.path.exists(dashboard_dir):
        print(f"❌ Dashboard directory '{dashboard_dir}' not found!")
        print("Make sure you're running this from the project root directory.")
        return
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # Start Flask app
        print("Dashboard will be available at: http://localhost:5000")
        print("Press Ctrl+C to stop the dashboard")
        print("=" * 60)
        subprocess.run([
            sys.executable, 
            os.path.join(dashboard_dir, 'app.py')
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()

# ===== run_dashboard.py (KÖK DİZİNDE) =====
# """
# Dashboard başlatma scripti
# Kullanım: python run_dashboard.py
# """

# import os
# import sys

# def main():
#     print("🌐 Starting Unified Threat Detection Dashboard...")
#     print("=" * 60)
    
#     # Check if web_dashboard exists
#     if not os.path.exists("web_dashboard"):
#         print("❌ Error: web_dashboard directory not found!")
#         print("Make sure you're in the project root directory.")
#         return
    
#     # Add current directory to Python path
#     sys.path.insert(0, os.getcwd())
    
#     # Import and run Flask app
#     try:
#         os.chdir("web_dashboard")
#         from app import app, initialize_platform
        
#         # Initialize platform
#         initialize_platform()
        
#         print("🚀 Dashboard starting at: http://localhost:5000")
#         print("Press Ctrl+C to stop")
#         print("=" * 60)
        
#         app.run(debug=True, host='0.0.0.0', port=5000)
        
#     except KeyboardInterrupt:
#         print("\n👋 Dashboard stopped")
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     main()