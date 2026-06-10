import csv
import os
import re
import requests
from bs4 import BeautifulSoup
from email_agent import send_email
from fleet_ai import draft_email_pitch_with_ollama

def find_emails_on_website(url):
    """
    Attempts to find email addresses on a given website.
    Checks the homepage and common 'contact' pages.
    """
    if not url:
        return None
    
    # Ensure URL starts with http
    if not url.startswith('http'):
        url = 'http://' + url

    emails = set()
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    try:
        # 1. Check the main page
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        emails.update(re.findall(email_regex, response.text))
        
        # 2. Look for a contact page
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'contact' in href:
                contact_url = href
                if not contact_url.startswith('http'):
                    from urllib.parse import urljoin
                    contact_url = urljoin(url, contact_url)
                
                res = requests.get(contact_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                emails.update(re.findall(email_regex, res.text))
                break # Just check the first contact link found
                
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        
    if emails:
        # Return the first one found
        return list(emails)[0]
    return None

def process_leads_and_send_emails(csv_path, limit=20):
    """
    Reads leads from CSV, discovers emails if missing, 
    generates a personalized pitch using AI, and sends emails.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    leads_processed = 0
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if leads_processed >= limit:
                break
            
            name = row.get('name') or row.get('business_name') or "Business Owner"
            website = row.get('website') or ""
            query = row.get('query') or "commercial mattress protection"
            recipient_email = row.get('email')

            # Automatic Email Discovery
            if not recipient_email and website:
                print(f"Attempting to discover email for {name} from {website}...")
                recipient_email = find_emails_on_website(website)
                if recipient_email:
                    print(f"Found email: {recipient_email}")

            print(f"Generating pitch for: {name}...")
            customer_data = f"Business: {name}, Website: {website}, Industry: {query}"
            pitch = draft_email_pitch_with_ollama(customer_data)
            
            if recipient_email:
                success = send_email(
                    recipient_email=recipient_email,
                    subject="Asset Protection for your Mattresses",
                    body=pitch
                )
                if success:
                    print(f"Successfully sent email to {name} ({recipient_email})")
                else:
                    print(f"Failed to send email to {name}")
            else:
                print(f"Skipping email for {name} because no email address was found.")
                print(f"--- PROPOSED PITCH FOR {name} ---\n{pitch}\n---------------------------------")
            
            leads_processed += 1

    print(f"\nFinished processing {leads_processed} leads.")

if __name__ == "__main__":
    CSV_FILE = "linkedin-outreach/refined_google_maps_leads.csv"
    process_leads_and_send_emails(CSV_FILE, limit=50)
