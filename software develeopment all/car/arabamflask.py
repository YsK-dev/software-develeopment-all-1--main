from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import csv
from datetime import datetime
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder
import platform
import pickle
import os
import joblib
import traceback

# Add this near the top of your file with other imports
MODEL_PATH = os.path.join(os.path.dirname(__file__), '/home/ysk/Desktop/software-develeopment-all-1--main/xgboost_classifier.joblib')

# Load the model (add this in your initialization section)
try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

app = Flask(__name__)
data_folder = "scraped_data"
os.makedirs(data_folder, exist_ok=True)
csv_file_path = os.path.join(data_folder, "arabaşişko.csv")

columns = [
    "ad_Id",
    "ad_date",
    "ad_loc1",
    "ad_loc2",
    "brand",
    "series",
    "model",
    "year",
    "mileage",
    "transmission",
    "fuel_type",
    "body_type",
    "color",
    "engine_capacity",
    "engine_power",
    "drive_type",
    "vehicle_condition",
    "fuel_consumption",
    "fuel_tank",
    "paint/replacement",
    "trade_in",
    "seller_type",
    "seller_name",
    "ad_price",
    "ad_url"
]

key_to_column = {
    "İlan No": "ad_Id",
    "İlan Tarihi": "ad_date",
    "Marka": "brand",
    "Seri": "series",
    "Model": "model",
    "Yıl": "year",
    "Kilometre": "mileage",
    "Vites Tipi": "transmission",
    "Yakıt Tipi": "fuel_type",
    "Kasa Tipi": "body_type",
    "Renk": "color",
    "Motor Hacmi": "engine_capacity",
    "Motor Gücü": "engine_power",
    "Çekiş": "drive_type",
    "Araç Durumu": "vehicle_condition",
    "Ortalama Yakıt Tüketimi": "fuel_consumption",
    "Yakıt Deposu": "fuel_tank",
    "Boya-değişen": "paint/replacement",
    "Takasa Uygun": "trade_in",
    "Kimden": "seller_type"
}

def wait_for_element_or_refresh(driver, timeout, locator):
    for attempt in range(3):
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            print(f"Attempt {attempt + 1}: Timeout waiting for element. Refreshing page.")
            driver.refresh()
    print("Element not found after 3 attempts. Skipping.")
    return False

def get_geckodriver_path():
    system = platform.system()
    if system == "Linux":
        # Try common Linux paths
        possible_paths = [
            "/usr/bin/geckodriver",
            "/usr/local/bin/geckodriver",
            os.path.expanduser("~/bin/geckodriver"),
            os.path.expanduser("~/.local/bin/geckodriver")
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/usr/local/bin/geckodriver",
            os.path.expanduser("~/bin/geckodriver"),
            os.path.expanduser("~/.local/bin/geckodriver")
        ]
    else:  # Windows
        possible_paths = [
            "C:\\geckodriver.exe",
            os.path.expanduser("~\\geckodriver.exe")
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise WebDriverException("Geckodriver not found. Please install geckodriver and make sure it's in your PATH or specify the path manually.")

def get_chromedriver_path():
    system = platform.system()
    if system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/chromedriver",
            "/opt/homebrew/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            os.path.expanduser("~/bin/chromedriver"),
            os.path.expanduser("~/.local/bin/chromedriver")
        ]
    elif system == "Linux":
        possible_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/lib/chromium-browser/chromedriver",
            "/usr/lib/chromium/chromedriver",
            os.path.expanduser("~/bin/chromedriver"),
            os.path.expanduser("~/.local/bin/chromedriver")
        ]
    else:  # Windows
        possible_paths = [
            "C:\\chromedriver.exe",
            "C:\\Program Files\\chromedriver.exe",
            "C:\\Program Files (x86)\\chromedriver.exe",
            os.path.expanduser("~\\chromedriver.exe")
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise WebDriverException("ChromeDriver not found. Please install ChromeDriver and make sure it's in your PATH.")

def scrape_ads():
    try:
        print("Starting scraping process...")
        
        # Configure Chrome options for Brave
        options = Options()
        options.add_argument('--headless=new')  # New headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set Brave browser path for Arch Linux
        options.binary_location = "/usr/bin/google-chrome-stable"
        
        # Initialize WebDriver with error handling
        try:
            # Try system chromedriver first
            service = Service(executable_path="/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            print("WebDriver initialized successfully with system chromedriver")
        except Exception as e:
            print(f"Error with system chromedriver: {e}")
            try:
                # Try alternative path
                service = Service(executable_path="/usr/local/bin/chromedriver")
                driver = webdriver.Chrome(service=service, options=options)
                print("WebDriver initialized successfully with alternative path")
            except Exception as e:
                print(f"Error with alternative path: {e}")
                try:
                    # Try using Brave's built-in chromedriver
                    service = Service(executable_path="/usr/lib/brave-browser/chromedriver")
                    driver = webdriver.Chrome(service=service, options=options)
                    print("WebDriver initialized successfully with Brave's chromedriver")
                except Exception as e:
                    print(f"Error with Brave's chromedriver: {e}")
                    raise Exception("Could not initialize WebDriver. Please make sure chromedriver is installed and in your PATH.")

        # Initialize or load existing data
        df_existent = pd.DataFrame(columns=columns)
        if os.path.exists(csv_file_path):
            df_existent = pd.read_csv(csv_file_path)
            print(f"Loaded {len(df_existent)} existing records")

        # Start scraping with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                base_url = "https://www.arabam.com/ikinci-el/otomobil"
                print(f"Attempt {attempt + 1}: Accessing {base_url}")
                driver.get(base_url)
                time.sleep(5)  # Wait for page to load
                
                # Wait for the listings to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.listing-list-item"))
                )
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise Exception("Failed to access the website after multiple attempts")
                time.sleep(2)  # Wait before retrying

        # Get all car listings on the first page
        try:
            car_listings = driver.find_elements(By.CSS_SELECTOR, "tr.listing-list-item")
            print(f"Found {len(car_listings)} cars on the first page")
            
            if len(car_listings) == 0:
                print("No car listings found. The page might have changed its structure.")
                driver.quit()
                return False
                
        except Exception as e:
            print(f"Error finding car listings: {e}")
            driver.quit()
            return False

        for car in car_listings:
            try:
                # Get car URL
                car_url = car.find_element(By.TAG_NAME, 'a').get_attribute('href')
                print(f"Processing car: {car_url}")
                
                # Open car page in new tab
                driver.execute_script("window.open(arguments[0]);", car_url)
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)  # Increased wait time for page load

                # Initialize car data
                car_data = {column: "Unspecified" for column in columns}
                
                # Get basic information with explicit waits
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='desktop-information-price']"))
                    )
                    car_data["ad_price"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='desktop-information-price']").text
                    car_data["brand"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='desktop-information-brand']").text
                    car_data["model"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='desktop-information-model']").text
                    car_data["year"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='desktop-information-year']").text
                    car_data["mileage"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='desktop-information-mileage']").text
                except Exception as e:
                    print(f"Error getting basic info: {e}")

                # Get additional details
                try:
                    details = driver.find_elements(By.CSS_SELECTOR, ".property-item")
                    for detail in details:
                        try:
                            key = detail.find_element(By.CSS_SELECTOR, ".property-key").text
                            value = detail.find_element(By.CSS_SELECTOR, ".property-value").text
                            if key in key_to_column:
                                car_data[key_to_column[key]] = value
                        except:
                            continue
                except Exception as e:
                    print(f"Error getting details: {e}")

                # Save the data
                new_df = pd.DataFrame([car_data])
                if not df_existent.empty:
                    df_existent['ad_Id'] = df_existent['ad_Id'].astype(str)
                    new_df['ad_Id'] = new_df['ad_Id'].astype(str)
                
                if new_df['ad_Id'].iloc[0] not in df_existent['ad_Id'].values:
                    new_df.to_csv(csv_file_path, mode='a', header=not os.path.exists(csv_file_path), index=False)
                    print("New car data saved successfully")
                else:
                    print("Car already exists in database")

                # Close the tab and switch back
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
            except Exception as e:
                print(f"Error processing car: {e}")
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except:
                    pass
                continue

        driver.quit()
        print("Scraping completed successfully")
        return True

    except Exception as e:
        print(f"Error in scrape_ads: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-scraper', methods=['POST'])
def start_scraper():
    try:
        scrape_ads()
        return jsonify({"message": "Scraping completed successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/view-data', methods=['GET'])
def view_data():
    try:
        if os.path.exists(csv_file_path):
            print(f"Reading data from {csv_file_path}")
            df = pd.read_csv(csv_file_path)
            print(f"Found {len(df)} records")
            
            # Clean and format the data
            df = df.replace('Unspecified', None)
            
            # Format prices - convert to numeric first, then format
            df['ad_price'] = pd.to_numeric(df['ad_price'].str.replace(' TL', '').str.replace('.', ''), errors='coerce')
            df['ad_price'] = df['ad_price'].apply(lambda x: f"{x:,.0f} TL" if pd.notnull(x) else "N/A")
            
            # Format mileage - convert to numeric first, then format
            df['mileage'] = pd.to_numeric(df['mileage'].str.replace(' km', '').str.replace('.', ''), errors='coerce')
            df['mileage'] = df['mileage'].apply(lambda x: f"{x:,.0f} km" if pd.notnull(x) else "N/A")
            
            # Convert to list of dictionaries for template
            cars = df.to_dict('records')
            
            return render_template('view_data.html', data=cars)
        else:
            print(f"Data file not found at {csv_file_path}")
            return render_template('view_data.html', data=None)
    except Exception as e:
        print(f"Error in view_data: {e}")
        return render_template('view_data.html', data=None, error=str(e))

# Load these at startup
model = joblib.load('xgboost_classifier.joblib') 
encoders = {}
# Define the features your model expects (from your PKL file)
features = [
    'mileage', 'year', 'vehicle_condition', 'fuel_tank', 'drive_type',
    'fuel_consumption', 'series', 'engine_capacity', 'trade_in',
    'transmission', 'brand', 'color', 'body_type', 'model',
    'fuel_type', 'seller_type', 'engine_power', 'vehicle_age',
    'is_original'
]

# Function to preprocess data for classification
def preprocess_data_for_classification(data):
    """Preprocess data to match classifier training format"""
    print("Starting data preprocessing...")
    print("Input data:", data)
    
    if isinstance(data, dict):
        data = pd.DataFrame([data])
    
    # Handle missing values
    data = data.replace('Unspecified', np.nan)
    print("Data after handling missing values:", data)
    
    # Convert numeric columns
    numeric_columns = ['mileage', 'year', 'fuel_tank', 'engine_capacity', 'engine_power']
    for col in numeric_columns:
        if col in data.columns:
            try:
                data[col] = pd.to_numeric(data[col].astype(str).str.replace('[^\d.]', '', regex=True), errors='coerce')
                print(f"Converted {col} to numeric:", data[col].iloc[0])
            except Exception as e:
                print(f"Error converting {col}: {str(e)}")
    
    # Add derived features
    try:
        data['vehicle_age'] = datetime.now().year - data['year']
        print("Added vehicle_age:", data['vehicle_age'].iloc[0])
    except Exception as e:
        print(f"Error calculating vehicle_age: {str(e)}")
    
    # Handle paint/replacement column
    paint_col = 'paint/replacement' if 'paint/replacement' in data.columns else 'paint_replaced'
    try:
        data['is_original'] = data[paint_col].apply(
            lambda x: 1 if pd.notna(x) and 'orjinal' in str(x).lower() else 0
        )
        print("Added is_original:", data['is_original'].iloc[0])
    except Exception as e:
        print(f"Error calculating is_original: {str(e)}")
    
    # Drop unused columns
    cols_to_drop = ['ad_url', 'ad_Id', 'seller_name', 'ad_date', paint_col, 
                   'ad_loc1', 'ad_loc2', 'ad_price']
    for col in cols_to_drop:
        if col in data.columns:
            data = data.drop(col, axis=1)
    
    # Ensure all required columns exist
    required_columns = [
        'mileage', 'year', 'vehicle_condition', 'fuel_tank', 'drive_type',
        'fuel_consumption', 'series', 'engine_capacity', 'trade_in',
        'transmission', 'brand', 'color', 'body_type', 'model',
        'fuel_type', 'seller_type', 'engine_power', 'vehicle_age',
        'is_original'
    ]
    
    for col in required_columns:
        if col not in data.columns:
            data[col] = np.nan
            print(f"Added missing column: {col}")
    
    print("Final preprocessed data:", data)
    return data

# Update your prediction function
def predict_car_price(car_data):
    try:
        print("\nStarting price prediction...")
        print("Input car data:", car_data)
        
        # Preprocess the input data
        processed_data = preprocess_data_for_classification(car_data)
        print("Processed data shape:", processed_data.shape)
        print("Processed data columns:", processed_data.columns.tolist())
        
        # Load the model
        print("Loading model...")
        model_path = '/home/ysk/Desktop/software-develeopment-all-1--main/xgboost_classifier.joblib'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        model = joblib.load(model_path)
        print("Model loaded successfully")
        
        # Make prediction
        print("Making prediction...")
        category_idx = model.predict(processed_data)[0]
        print(f"Predicted category: {category_idx}")
        
        # Get brand and adjust price range accordingly
        brand = car_data.get('brand', '').lower()
        is_luxury = brand in ['bmw', 'mercedes', 'audi', 'volvo', 'lexus', 'jaguar', 'land rover', 'porsche']
        
        # Base price ranges
        price_ranges = {
            0: (0, 500000),        # 'Very Low'
            1: (500000, 750000),   # 'Low'
            2: (750000, 1000000),  # 'Medium'
            3: (1000000, 1500000), # 'High'
            4: (1500000, float('inf'))  # 'Premium'
        }
        
        # Adjust ranges for luxury brands
        if is_luxury:
            print(f"Adjusting price range for luxury brand: {brand}")
            # Shift the category up by 1 for luxury brands
            category_idx = min(category_idx + 1, 4)
            # Further adjust based on model and year
            if brand == 'bmw':
                if '3 serisi' in car_data.get('model', '').lower():
                    category_idx = min(category_idx + 1, 4)
                elif '5 serisi' in car_data.get('model', '').lower():
                    category_idx = min(category_idx + 2, 4)
                elif '7 serisi' in car_data.get('model', '').lower():
                    category_idx = 4  # Always premium for 7 series
        
        # Get the price range for the predicted category
        low, high = price_ranges[category_idx]
        predicted_price = (low + high) / 2
        
        # Additional adjustments based on car condition
        if car_data.get('vehicle_condition', '').lower() == 'sıfır':
            predicted_price *= 1.2  # 20% increase for new condition
        elif car_data.get('vehicle_condition', '').lower() == 'az kullanılmış':
            predicted_price *= 1.1  # 10% increase for lightly used
        
        # Ensure minimum price for luxury brands
        if is_luxury:
            predicted_price = max(predicted_price, 500000)
        
        print(f"Adjusted predicted price range: {low} - {high}")
        print(f"Final predicted price: {predicted_price}")
        
        return predicted_price
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        print("Stack trace:", traceback.format_exc())
        # Fallback to a reasonable price if prediction fails
        return 750000

@app.route('/predict', methods=['GET'])
def predict():
    return render_template('predict.html')

@app.route('/estimate-price', methods=['POST'])
def estimate_price():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
            
        # Scrape car data
        result = scrape_single_car(url)
        if not result["success"]:
            return jsonify({"error": result["error"]}), 500
            
        car_data = result["data"]
        actual_price = result["price"]
        
        # Make prediction
        predicted_price = predict_car_price(car_data)
        
        # Calculate price difference
        price_difference = actual_price - predicted_price
        price_difference_percentage = (price_difference / actual_price) * 100
        
        return jsonify({
            "success": True,
            "actual_price": f"{actual_price:,.0f} TL",
            "predicted_price": f"{predicted_price:,.0f} TL",
            "price_difference": f"{price_difference:,.0f} TL",
            "price_difference_percentage": f"{price_difference_percentage:.1f}%",
            "car_data": car_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def scrape_single_car(url):
    try:
        print(f"Starting to scrape car data from: {url}")
        
        
        
        
        # Configure Chrome options
        options = Options()
        
        # Create a unique user data directory
        import tempfile
        import uuid
        import os
        import shutil
        
        # Use UUID to ensure uniqueness
        temp_dir = os.path.join(tempfile.gettempdir(), f"chrome_temp_{uuid.uuid4().hex}")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Using temp directory: {temp_dir}")
        
        # Set the user data directory
        options.add_argument(f'--user-data-dir={temp_dir}')
        
        # Headless mode settings
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Performance optimizations
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Timeout settings - important to handle renderer timeouts
        options.add_argument('--disable-hang-monitor')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-prompt-on-repost')
        
        # Memory and performance optimizations
        options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--enable-features=NetworkServiceInProcess')
        
        # Window size and user agent
        options.add_argument('--window-size=1280,720')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36')
        
        # Set browser path based on platform
        if platform.system() == "Darwin":  # macOS
            options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif platform.system() == "Linux":
            options.binary_location = "/usr/bin/google-chrome-stable"
        else:  # Windows
            options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        
        # Get ChromeDriver path
        chromedriver_path = get_chromedriver_path()
        print(f"Using ChromeDriver at: {chromedriver_path}")
        
        # Initialize WebDriver with retry mechanism and better error handling
        max_retries = 3
        retry_count = 0
        last_error = None
        driver = None
        
        while retry_count < max_retries:
            try:
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
                print("WebDriver initialized successfully")
                break
            except Exception as e:
                last_error = e
                retry_count += 1
                print(f"Attempt {retry_count} failed: {str(e)}")
                
                # Clean up after failure
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = None
                
                # Remove the temp directory and try again with a new one
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    temp_dir = os.path.join(tempfile.gettempdir(), f"chrome_temp_{uuid.uuid4().hex}")
                    os.makedirs(temp_dir, exist_ok=True)
                    options.add_argument(f'--user-data-dir={temp_dir}')
                    print(f"Created new temp directory: {temp_dir}")
                except:
                    pass
                
                # Additional cleanup between attempts
                

                
                if retry_count < max_retries:
                    time.sleep(3)  # Wait longer between attempts
                    continue
                else:
                    raise Exception(f"Failed to initialize WebDriver after {max_retries} attempts. Last error: {str(last_error)}")
        
        # Continue only if driver initialized successfully
        if not driver:
            raise Exception("Driver initialization failed")
            
        try:
            # Set page load timeout (increased for better reliability)
            driver.set_page_load_timeout(45)
            driver.set_script_timeout(45)
            
            # Navigate to URL with retry mechanism and timeout handling
            page_load_retries = 3
            for attempt in range(page_load_retries):
                try:
                    print(f"Loading URL (attempt {attempt+1}): {url}")
                    driver.get(url)
                    print("Page loaded successfully")
                    break
                except Exception as e:
                    if attempt == page_load_retries - 1:
                        raise Exception(f"Failed to load page after {page_load_retries} attempts: {str(e)}")
                    print(f"Page load attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(5)  # Increased wait time between page load attempts
            
            # Wait for page to fully load and stabilize
            time.sleep(5)
            
            # Initialize car data
            car_data = {column: "Unspecified" for column in columns}
            
            # Get basic information with more robust waiting
            try:
                wait = WebDriverWait(driver, 10)
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='desktop-information-price']"))
                )
                
                # Extract price and convert to numeric
                price_text = price_element.text
                price = float(price_text.replace(' TL', '').replace('.', '').replace(',', '.'))
                
                # Get other car details with explicit waits for each element
                car_data["brand"] = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div:nth-child(5) > div.container > div > div.product-detail > div.product-detail-wrapper > div.product-properties-container > div.product-properties > div.product-properties-details.linear-gradient > div:nth-child(3) > div.property-value"))
                ).text
                
                car_data["model"] = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div:nth-child(5) > div.container > div > div.product-detail > div.product-detail-wrapper > div.product-properties-container > div.product-properties > div.product-properties-details.linear-gradient > div:nth-child(5) > div.property-value"))
                ).text
                
                car_data["year"] = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div:nth-child(5) > div.container > div > div.product-detail > div.product-detail-wrapper > div.product-properties-container > div.product-properties > div.product-properties-details.linear-gradient > div:nth-child(6) > div.property-value"))
                ).text
                
                car_data["mileage"] = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#wrapper > div:nth-child(5) > div.container > div > div.product-detail > div.product-detail-wrapper > div.product-properties-container > div.product-properties > div.product-properties-details.linear-gradient > div:nth-child(7) > div.property-value"))
                ).text
                
            except Exception as e:
                print(f"Error getting basic car information: {str(e)}")
                # Take a screenshot for debugging
                try:
                    screenshot_path = os.path.join(tempfile.gettempdir(), f"scraper_debug_{uuid.uuid4().hex}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Debug screenshot saved to {screenshot_path}")
                except:
                    pass
                raise
            
            # Get additional details with error handling for each property
            try:
                details = driver.find_elements(By.CSS_SELECTOR, ".property-item")
                for detail in details:
                    try:
                        key = detail.find_element(By.CSS_SELECTOR, ".property-key").text
                        value = detail.find_element(By.CSS_SELECTOR, ".property-value").text
                        if key in key_to_column:
                            car_data[key_to_column[key]] = value
                    except Exception as detail_error:
                        print(f"Skipping property due to error: {str(detail_error)}")
                        continue
            except Exception as e:
                print(f"Warning: Error getting additional details: {str(e)}")
                # Continue with partial data
            
            return {
                "success": True,
                "price": price,
                "data": car_data
            }
            
        except Exception as e:
            print(f"Error scraping car data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Always ensure browser is closed and temp directories cleaned up
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"Error during driver quit: {str(quit_error)}")
                driver = None
            
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"Removed temp directory: {temp_dir}")
            except Exception as cleanup_error:
                print(f"Error during temp directory cleanup: {str(cleanup_error)}")
            
            # Final process cleanup
  
            
    except Exception as e:
        print(f"Error in scrape_single_car: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == '__main__':
    app.run(debug=True)