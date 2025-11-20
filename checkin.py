from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os


def setup_driver(headless=False):
    """Setup Chrome driver with options"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    
    return webdriver.Chrome(options=chrome_options)


def checkin(email, password, headless=False):
    """Automated check-in"""
    print("🚀 Starting check-in automation...")
    driver = setup_driver(headless=headless)
    
    try:
        # Step 1: Navigate to login page
        print("📍 Navigating to login page...")
        driver.get('https://payroll.razorpay.com/login')
        time.sleep(2)
        
        # Step 2: Login
        print("✍️  Logging in...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.clear()
        email_field.send_keys(email)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        time.sleep(5)
        
        # Step 3: Wait for dashboard
        WebDriverWait(driver, 15).until(
            EC.url_contains('/dashboard')
        )
        print("✅ Login successful!")
        
        # Step 4: Navigate to Attendance page
        print("📍 Navigating to Attendance page...")
        attendance_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/attendance')]"))
        )
        attendance_link.click()
        time.sleep(3)
        
        print(f"✅ Current URL: {driver.current_url}")
        
        # Step 5: Check if already checked in
        print("🔍 Checking attendance status...")
        
        try:
            # Look for "Check Out" button - means already checked in
            checkout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Check Out')]")
            print("✅ Already checked in for today!")
            print(f"⏰ Check-in completed at {datetime.now().strftime('%H:%M:%S')}")
            driver.save_screenshot('already_checked_in.png')
            return True
            
        except:
            # Not checked in yet, look for check-in option
            print("⏳ Not checked in yet, proceeding with check-in...")
        
        # Step 6: Try to find and click check-in button
        try:
            # Wait for any check-in related button
            checkin_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(translate(text(), 'CHECKIN', 'checkin'), 'check in')]"))
            )
            
            driver.save_screenshot('before_checkin.png')
            print("✅ Found check-in button, clicking...")
            checkin_button.click()
            time.sleep(3)
            
            driver.save_screenshot('after_checkin.png')
            print(f"🎉 Successfully checked in at {datetime.now().strftime('%H:%M:%S')}")
            return True
            
        except:
            # If no check-in button found, might already be checked in automatically
            print("⚠️  No check-in button found. Checking status...")
            driver.save_screenshot('no_button_found.png')
            
            # Check if attendance is already marked in the banner
            try:
                marked_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Your attendance has been marked')]")
                print("✅ Attendance already marked for today!")
                return True
            except:
                print("❌ Could not determine check-in status")
                return False
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        driver.save_screenshot('error_screenshot.png')
        print("📸 Error screenshot saved")
        print(f"📍 Current URL: {driver.current_url}")
        return False
        
    finally:
        if not headless:
            print("⏸️  Waiting 5 seconds before closing...")
            time.sleep(5)
        driver.quit()
        print("✅ Browser closed")


if __name__ == "__main__":
    # Try to load .env file if it exists (for local development only)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("ℹ️  Running without .env (using environment variables)")
    
    # Get credentials from environment variables
    EMAIL = os.environ.get('RAZORPAY_EMAIL')
    PASSWORD = os.environ.get('RAZORPAY_PASSWORD')
    
    if not EMAIL or not PASSWORD:
        print("❌ Error: RAZORPAY_EMAIL and RAZORPAY_PASSWORD must be set")
        exit(1)
    
    print("=" * 50)
    print("🧪 ATTENDANCE AUTO CHECK-IN")
    print("=" * 50)
    
    # Use headless mode in CI environment
    is_ci = os.environ.get('CI', 'false').lower() == 'true'
    success = checkin(EMAIL, PASSWORD, headless=is_ci)
    
    if success:
        print("\n✅ Check-in process completed successfully!")
        exit(0)
    else:
        print("\n❌ Check-in failed! Check screenshots for details")
        exit(1)
