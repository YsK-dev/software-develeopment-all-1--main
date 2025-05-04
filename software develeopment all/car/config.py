import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Scraper settings
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    DATA_FOLDER = os.environ.get('DATA_FOLDER', 'scraped_data')
    MAX_SCRAPE_RETRIES = int(os.environ.get('MAX_SCRAPE_RETRIES', 3))