import pandas as pd
import json
import os

def create_demo_data():
    """Demo verileri oluşturur"""
    
    # Sample emails
    emails = [
        {
            "subject": "URGENT: Account Suspended!",
            "body": "Your PayPal account will be suspended. Click here: http://payp4l-fake.tk/verify",
            "sender": "security@payp4l-fake.com",
            "label": 1
        },
        {
            "subject": "Team Meeting",
            "body": "Hi team, we have a meeting tomorrow at 10 AM.",
            "sender": "manager@company.com", 
            "label": 0
        }
    ]
    
    # Sample web logs
    web_logs = [
        "203.0.113.45 - - [10/Oct/2023:14:01:01 +0200] \"POST /admin/login HTTP/1.1\" 401 1234 \"-\" \"Python-urllib/3.6\"",
        "192.168.1.100 - - [10/Oct/2023:13:55:36 +0200] \"GET / HTTP/1.1\" 200 2326 \"-\" \"Mozilla/5.0 (Windows NT 10.0; Win64; x64)\""
    ]
    
    # Klasörleri oluştur
    os.makedirs("data/samples", exist_ok=True)
    
    # Save demo data
    pd.DataFrame(emails).to_csv("data/samples/demo_emails.csv", index=False)
    
    with open("data/samples/demo_web_logs.txt", "w") as f:
        f.write("\n".join(web_logs))
    
    print("✅ Demo data created successfully!")

if __name__ == "__main__":
    create_demo_data()