"""
Selenium ile tüm sayfaların tam ekran görüntülerini alma
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

REPORT_DIR = r"c:\Users\hakan\UnifiedCyberThreatDetectionSystem\docs\professor_report\screenshots"
BASE_URL = "http://localhost:5000"

def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def take_fullpage_screenshot(driver, filename):
    """Tam sayfa ekran görüntüsü al"""
    # Sayfanın yüklenmesini bekle
    time.sleep(2)
    
    # Scroll to top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)
    
    # Get total height
    total_height = driver.execute_script("return document.body.scrollHeight")
    
    # Set window size to capture full page
    driver.set_window_size(1920, min(total_height + 200, 4000))
    time.sleep(1)
    
    # Screenshot
    filepath = os.path.join(REPORT_DIR, filename)
    driver.save_screenshot(filepath)
    print(f"✅ Saved: {filename}")
    
    # Reset window size
    driver.set_window_size(1920, 1080)
    return filepath

def main():
    # Create directory
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    driver = setup_driver()
    
    try:
        # 1. Dashboard
        driver.get(BASE_URL)
        time.sleep(3)
        take_fullpage_screenshot(driver, "01_dashboard.png")
        
        # 2. Email Analysis
        driver.find_element(By.CSS_SELECTOR, 'a[href="#email-analysis"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "02_email_analysis.png")
        
        # 3. Web Analysis
        driver.find_element(By.CSS_SELECTOR, 'a[href="#web-analysis"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "03_web_analysis.png")
        
        # 4. Correlation Analysis
        driver.find_element(By.CSS_SELECTOR, 'a[href="#correlation-analysis"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "04_correlation_analysis.png")
        
        # 5. Model Comparison
        driver.find_element(By.CSS_SELECTOR, 'a[href="#model-comparison"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "05_model_comparison.png")
        
        # 6. Reports
        driver.find_element(By.CSS_SELECTOR, 'a[href="#reports"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "06_reports.png")
        
        # 7. Settings
        driver.find_element(By.CSS_SELECTOR, 'a[href="#settings"]').click()
        time.sleep(2)
        take_fullpage_screenshot(driver, "07_settings.png")
        
        print("\n🎉 Tüm ekran görüntüleri alındı!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
