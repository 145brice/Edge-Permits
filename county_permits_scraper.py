#!/usr/bin/env python3
"""
County Building Permits Scraper
Scrapes daily building permits from Bexar, Hamilton, Davidson, and Travis counties.

Requirements:
- pip install selenium beautifulsoup4 requests lxml pyyaml webdriver-manager

Usage:
- python county_permits_scraper.py [--sort]  # --sort to generate sorted versions
- Or schedule with cron: 0 6 * * * /usr/bin/python3 /path/to/county_permits_scraper.py

Output: CSV files in data/ directory with timestamp and optional sorted versions
"""

import os
import sys
import time
import random
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import csv
import re
import yaml
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CountyPermitScraper:
    def __init__(self, config_path='config.yaml'):
        self.config = self.load_config(config_path)
        self.user_agents = self.config['global']['user_agents']
        self.delays = self.config['global']['delays']
        self.csv_headers = self.config['global']['csv_headers']
        self.setup_directories()

    def load_config(self, config_path):
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file {config_path} not found")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def setup_directories(self):
        """Create necessary directories."""
        Path('data').mkdir(exist_ok=True)
        Path('logs').mkdir(exist_ok=True)

    def get_driver(self):
        """Setup Chrome driver with options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
        chrome_options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(self.user_agents)})
        return driver

    def scrape_bexar(self):
        """Scrape Bexar County (San Antonio) permits."""
        county_config = self.config['counties']['bexar']
        driver = self.get_driver()

        try:
            logging.info("Starting Bexar County scrape")
            driver.get(county_config['base_url'])

            # Navigate to search permits
            search_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, county_config['selectors']['search_link']))
            )
            search_link.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            # Set date range to last 7 days
            today = datetime.now()
            week_ago = today - timedelta(days=7)

            from_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['from_date'])
            from_date_input.clear()
            from_date_input.send_keys(week_ago.strftime(county_config['date_format']))

            to_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['to_date'])
            to_date_input.clear()
            to_date_input.send_keys(today.strftime(county_config['date_format']))

            # Submit search
            submit_btn = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['submit'])
            submit_btn.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            # Parse results
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            permits = self.parse_accela_results(soup, 'Bexar County')

            self.save_to_csv(permits, 'bexar')
            logging.info(f"Scraped {len(permits)} permits from Bexar County")

        except Exception as e:
            logging.error(f"Error scraping Bexar County: {e}")
        finally:
            driver.quit()

    def scrape_hamilton(self):
        """Scrape Hamilton County (Chattanooga) permits."""
        county_config = self.config['counties']['hamilton']
        driver = self.get_driver()

        try:
            logging.info("Starting Hamilton County scrape")
            driver.get(county_config['base_url'])

            search_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, county_config['selectors']['search_link']))
            )
            search_link.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            today = datetime.now()
            week_ago = today - timedelta(days=7)

            from_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['from_date'])
            from_date_input.clear()
            from_date_input.send_keys(week_ago.strftime(county_config['date_format']))

            to_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['to_date'])
            to_date_input.clear()
            to_date_input.send_keys(today.strftime(county_config['date_format']))

            submit_btn = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['submit'])
            submit_btn.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            permits = self.parse_accela_results(soup, 'Hamilton County')

            self.save_to_csv(permits, 'hamilton')
            logging.info(f"Scraped {len(permits)} permits from Hamilton County")

        except Exception as e:
            logging.error(f"Error scraping Hamilton County: {e}")
        finally:
            driver.quit()

    def scrape_davidson(self):
        """Scrape Davidson County (Nashville) permits."""
        county_config = self.config['counties']['davidson']
        driver = self.get_driver()

        try:
            logging.info("Starting Davidson County scrape")
            driver.get(county_config['base_url'])
            time.sleep(5)  # Wait for JS to load

            # Click Advanced Search
            advanced_search = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, county_config['selectors']['advanced_search_link']))
            )
            advanced_search.click()
            time.sleep(3)

            # Select "Issued" status
            issued_radio = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['status_issued'])
            issued_radio.click()

            # Set issued date range to last 7 days
            today = datetime.now()
            week_ago = today - timedelta(days=7)

            # Use JavaScript to set the date values
            driver.execute_script(f"document.getElementById('issuedDateFrom').value = '{week_ago.strftime('%m/%d/%Y')}';")
            driver.execute_script(f"document.getElementById('issuedDateTo').value = '{today.strftime('%m/%d/%Y')}';")
            time.sleep(2)  # Wait for date processing
            time.sleep(1)  # Wait for date picker to close

            # Click outside to close any date pickers
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(1)

            # Submit search
            search_btn = driver.find_element(By.XPATH, f"//button[text()='{county_config['selectors']['search_button']}']")
            search_btn.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            # Parse results
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            permits = self.parse_nashville_results(soup, 'Davidson County')

            self.save_to_csv(permits, 'davidson')
            logging.info(f"Scraped {len(permits)} permits from Davidson County")

        except Exception as e:
            logging.error(f"Error scraping Davidson County: {e}")
        finally:
            driver.quit()

    def scrape_travis(self):
        """Scrape Travis County (Austin) permits."""
        county_config = self.config['counties']['travis']
        driver = self.get_driver()

        try:
            logging.info("Starting Travis County scrape")
            driver.get(county_config['fallback_url'])

            search_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, county_config['selectors']['search_link']))
            )
            search_link.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            today = datetime.now()
            week_ago = today - timedelta(days=7)

            from_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['from_date'])
            from_date_input.clear()
            from_date_input.send_keys(week_ago.strftime(county_config['date_format']))

            to_date_input = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['to_date'])
            to_date_input.clear()
            to_date_input.send_keys(today.strftime(county_config['date_format']))

            submit_btn = driver.find_element(By.CSS_SELECTOR, county_config['selectors']['submit'])
            submit_btn.click()
            time.sleep(random.uniform(*self.delays['between_actions']))

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            permits = self.parse_accela_results(soup, 'Travis County')

            self.save_to_csv(permits, 'travis')
            logging.info(f"Scraped {len(permits)} permits from Travis County")

        except Exception as e:
            logging.error(f"Error scraping Travis County: {e}")
        finally:
            driver.quit()

    def parse_accela_results(self, soup, county_name):
        """Parse Accela search results."""
        permits = []

        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    permit = {
                        'permit_number': cols[0].get_text().strip(),
                        'issue_date': cols[1].get_text().strip(),
                        'address': cols[2].get_text().strip(),
                        'work_type': cols[3].get_text().strip(),
                        'contractor': cols[4].get_text().strip() if len(cols) > 4 else '',
                        'valuation': cols[5].get_text().strip() if len(cols) > 5 else ''
                    }
                    permits.append(permit)

        return permits

    def parse_nashville_results(self, soup, county_name):
        """Parse Nashville ePermits search results."""
        permits = []

        # Look for results in various formats
        # First try table format
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    permit = {
                        'permit_number': cols[0].get_text().strip(),
                        'issue_date': cols[1].get_text().strip() if len(cols) > 1 else '',
                        'address': cols[2].get_text().strip() if len(cols) > 2 else '',
                        'work_type': cols[3].get_text().strip() if len(cols) > 3 else '',
                        'contractor': cols[4].get_text().strip() if len(cols) > 4 else '',
                        'valuation': cols[5].get_text().strip() if len(cols) > 5 else ''
                    }
                    permits.append(permit)

        # If no table, look for divs or other structures
        if not permits:
            # Look for permit cards or list items
            permit_elements = soup.find_all(['div', 'li'], class_=re.compile(r'permit|result|record'))
            for elem in permit_elements:
                permit_text = elem.get_text()
                # Try to extract permit info from text
                # This is a fallback - Nashville's format may be different
                lines = permit_text.split('\n')
                if len(lines) >= 3:
                    permit = {
                        'permit_number': lines[0].strip(),
                        'issue_date': lines[1].strip() if len(lines) > 1 else '',
                        'address': lines[2].strip() if len(lines) > 2 else '',
                        'work_type': 'Unknown',
                        'contractor': '',
                        'valuation': ''
                    }
                    permits.append(permit)

        return permits

    def parse_csv_permits(self, content, county_name):
        """Parse CSV content from downloaded files."""
        permits = []
        lines = content.split('\n')

        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 6:
                    permit = {
                        'permit_number': parts[0].strip(),
                        'issue_date': parts[1].strip(),
                        'address': parts[2].strip(),
                        'work_type': parts[3].strip(),
                        'contractor': parts[4].strip(),
                        'valuation': parts[5].strip()
                    }
                    permits.append(permit)

        return permits

    def save_to_csv(self, permits, county_slug, generate_sorted=False):
        """Save permits to CSV file with timestamp."""
        if not permits:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"data/{county_slug}_permits_{timestamp}.csv"

        # Sort by issue date descending (newest first)
        try:
            permits.sort(key=lambda x: datetime.strptime(x['issue_date'], "%m/%d/%Y"), reverse=True)
        except ValueError:
            logging.warning(f"Could not sort permits for {county_slug} by date")

        with open(base_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
            writer.writeheader()
            writer.writerows(permits)

        logging.info(f"Saved {len(permits)} permits to {base_filename}")

        if generate_sorted:
            self.generate_sorted_versions(permits, county_slug, timestamp)

    def generate_sorted_versions(self, permits, county_slug, timestamp):
        """Generate sorted versions of the CSV."""
        sort_keys = {
            'date': lambda x: datetime.strptime(x['issue_date'], "%m/%d/%Y") if x['issue_date'] else datetime.min,
            'valuation': lambda x: float(re.sub(r'[^\d.]', '', x['valuation'])) if x['valuation'] else 0,
            'address': lambda x: x['address'].lower(),
            'contractor': lambda x: x['contractor'].lower(),
            'work_type': lambda x: x['work_type'].lower()
        }

        for sort_name, sort_func in sort_keys.items():
            sorted_permits = sorted(permits, key=sort_func, reverse=(sort_name in ['date', 'valuation']))
            filename = f"data/{county_slug}_permits_{timestamp}_sorted_{sort_name}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_headers)
                writer.writeheader()
                writer.writerows(sorted_permits)
            logging.info(f"Saved sorted {sort_name} version to {filename}")

    def run_all(self, generate_sorted=False):
        """Run scrapers for all counties."""
        logging.info("Starting full scrape cycle")

        self.scrape_bexar()
        time.sleep(random.uniform(*self.delays['between_counties']))

        self.scrape_hamilton()
        time.sleep(random.uniform(*self.delays['between_counties']))

        self.scrape_davidson()
        time.sleep(random.uniform(*self.delays['between_counties']))

        self.scrape_travis()

        logging.info("Completed full scrape cycle")

def main():
    parser = argparse.ArgumentParser(description='Scrape county building permits')
    parser.add_argument('--sort', action='store_true', help='Generate sorted versions of CSVs')
    args = parser.parse_args()

    scraper = CountyPermitScraper()
    scraper.run_all(generate_sorted=args.sort)

if __name__ == "__main__":
    main()