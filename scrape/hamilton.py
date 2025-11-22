import csv
import os
from datetime import datetime

def scrape_hamilton():
    """
    Mock scraper for Hamilton County permits.
    In a real implementation, this would scrape from Hamilton County's permit website.
    """
    permits = [
        {
            'county': 'Hamilton',
            'permit_number': 'HAM-001',
            'address': '321 Signal Mountain Rd, Chattanooga, TN',
            'permit_type': 'Residential New Construction',
            'estimated_value': 350000,
            'work_description': 'New single-family home construction'
        },
        {
            'county': 'Hamilton', 
            'permit_number': 'HAM-002',
            'address': '654 Market St, Chattanooga, TN',
            'permit_type': 'Commercial Addition',
            'estimated_value': 125000,
            'work_description': 'Retail store expansion'
        }
    ]
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Append to CSV
    with open('data/permits.csv', 'a', newline='') as csvfile:
        fieldnames = ['county', 'permit_number', 'address', 'permit_type', 'estimated_value', 'work_description', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is empty
        if os.stat('data/permits.csv').st_size == 0:
            writer.writeheader()
        
        for permit in permits:
            permit['date'] = datetime.now().strftime('%Y-%m-%d')
            writer.writerow(permit)
    
    return permits

if __name__ == '__main__':
    permits = scrape_hamilton()
    print(f"Scraped {len(permits)} permits from Hamilton County")
