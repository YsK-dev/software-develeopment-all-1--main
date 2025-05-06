
# 🚗 Car Scraper

### Overview

The **Car Ads Scraper** is a Python-based web scraper built using Selenium and Flask. It collects car advertisement data from [arabam.com](https://www.arabam.com) and stores the results in a CSV file. Users can trigger scraping tasks and view collected data through a user-friendly web interface.



## Table of Contents
1. [Features](#features)  
2. [Technologies Used](#technologies-used)  
3. [System Requirements](#system-requirements)  
4. [Installation](#installation)  
5. [Usage Instructions](#usage-instructions)  
6. [Project Structure](#project-structure)  
7. [Troubleshooting](#troubleshooting)  
8. [License](#license)  

---

## Features
- Scrape car ads, including key details like price, location, and specifications.
- Save data to a CSV file for further analysis.
- Web interface to manage scraping and view collected data.
- Supports multiple pages and handles dynamic content.

---

## Technologies Used
- **Python 3.8+**
- **Selenium** for web scraping.
- **Flask** for the web interface.
- **Pandas** for data manipulation.
- **Bootstrap** for front-end styling.

---

## System Requirements
### Hardware
- **CPU**: 2 GHz dual-core or better  
- **RAM**: 4 GB (8 GB recommended)  
- **Storage**: 100 MB free space  

### Software
- **Operating System**: Windows, macOS, or Linux  
- **Python**: Version 3.8 or higher  
- **Firefox**: Installed with matching `geckodriver`

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/car-ads-scraper.git
   cd car-ads-scraper
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Firefox and Geckodriver:
   - [Download Firefox](https://www.mozilla.org/firefox/)
   - [Download Geckodriver](https://github.com/mozilla/geckodriver/releases)
   - Ensure the `geckodriver` binary is in your PATH or specify its location in the script.

5. Start the Flask app:
   ```bash
   python app.py
   ```

6. Access the web interface at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Usage Instructions
### Web Interface
1. Navigate to the home page.
2. Click **Start Scraper** to begin scraping car ads.
3. After scraping, click **View Collected Data** to see the data in a table format.

### Data Storage
- Collected data is saved to `scraped_data/scraped_ads.csv`.

---

## Project Structure
```
car-ads-scraper/
│
├── arabamflask.py                # Main Flask application
├── scraped_data/         # Folder to store CSV data
├── templates/            # HTML templates for Flask
│   ├── index.html        # Home page
│   └── view_data.html    # Data display page
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Troubleshooting
### Common Issues
1. **"Unable to locate Geckodriver"**:
   - Ensure `geckodriver` is installed and in your PATH.
   - Update the `executable_path` in the script if necessary.

2. **Scraping is slow**:
   - The scraper intentionally includes delays to avoid getting blocked by the website.

3. **Data not displayed in the web interface**:
   - Ensure scraping is completed, and check if `scraped_data/scraped_ads.csv` contains data.

### Debugging
- Run the scraper directly to view browser actions:
   ```python
   python arabamflask.py
   ```
