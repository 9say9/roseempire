"""
Rose Empire Lead Gen: High-End Care Home Acquisition Script
Purpose:
1. Use Sarah (fleet_scraper) to find active Care Homes with websites.
2. Use Adeel (lead_pipeline) to qualify, deduplicate, and score them.
3. Export to outreach_master.csv for James (fleet_ai) to draft personalized pitches.
"""

import subprocess
import sys
from pathlib import Path

# Configuration
MISSION = "luxury care homes nursing homes UK mattress protector bulk buyers"
LIMIT = 20  # Increase for more leads
HEADED = True # Set to True for the first run to handle Google consent

def run_command(cmd):
    print(f"Executing: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error executing command:\n{result.stderr}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def main():
    print("🚀 Initializing Rose Empire High-End Lead Acquisition...")

    # Step 1: Sarah Scrape
    # We use --headed to ensure Google Maps consent is handled if needed
    print("\n[1/3] Sarah is hunting for high-end care home leads...")
    scrape_cmd = f'py -3 fleet_scraper.py --limit {LIMIT} --mission "{MISSION}" --headed'
    run_command(scrape_cmd)

    # Step 2: Adeel Qualify
    # This merges raw scrapes into the pipeline, filters by score, and exports
    print("\n[2/3] Adeel is qualifying and enriching lead data...")
    qualify_cmd = 'py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach'
    run_command(qualify_cmd)

    # Step 3: Status Report
    print("\n[3/3] Finalizing Acquisition Report...")
    outreach_file = Path("linkedin-outreach/outreach_master.csv")
    if outreach_file.exists():
        print(f"\n✅ SUCCESS: Leads have been synced to {outreach_file}")
        print("Next Steps:")
        print("1. Open the B2B Command Center (http://127.0.0.1:5050)")
        print("2. Select a lead from the Pipeline")
        print("3. Use James (AI Pitch Engine) to generate a tailored offer")
        print("4. Dispatch via SMTP")
    else:
        print("\n❌ FAILED: Outreach master file was not created. Check scraper output.")

if __name__ == "__main__":
    main()
