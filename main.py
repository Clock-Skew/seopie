import sys
import json
import os
import random
import time
import requests
from requests.exceptions import RequestException
from urllib.parse import urlparse
from meta_information_analyzer import MetaInformationAnalyzer
from page_quality_analyzer import PageQualityAnalyzer
from page_structure_analyzer import PageStructureAnalyzer
from link_structure_analyzer import LinkStructureAnalyzer
from server_configuration_analyzer import ServerConfigurationAnalyzer
from external_factors_analyzer import ExternalFactorsAnalyzer
from seo_score_calculator import SEOScoreCalculator
from image_analyzer import ImageAnalyzer
from page_speed_analyzer import PageSpeedAnalyzer
from schema_markup_analyzer import SchemaMarkupAnalyzer
from readability_analyzer import ReadabilityAnalyzer
from broken_links_analyzer import BrokenLinksAnalyzer

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
]


full_report = None

def random_delay():
    time.sleep(random.uniform(1, 3))

def random_user_agent():
    return random.choice(USER_AGENTS)

def display_banner():
    banner = r"""
      ::::::::  :::::::::: ::::::::  ::::::::: ::::::::::: :::::::::: 
    :+:    :+: :+:       :+:    :+: :+:    :+:    :+:     :+:         
   +:+        +:+       +:+    +:+ +:+    +:+    +:+          
  +#++:++#++ +#++:++#  +#+    +:+ +#++:++#+     +#+     +#++:++#      
        +#+ +#+       +#+    +#+ +#+           +#+     +#+            
#+#    #+# #+#       #+#    #+# #+#           #+#     #+#             
########  ########## ########  ###       ########### ##########       
    """
    print(banner)

def main_menu():
    print("\nWelcome to the SEO Analysis Tool!")
    print("Please select an option:")
    print("0. Change Target URL")
    print("1. Analyze Meta Information")
    print("2. Analyze Page Quality")
    print("3. Analyze Page Structure")
    print("4. Analyze Link Structure")
    print("5. Analyze Server Configuration")
    print("6. Analyze External Factors")
    print("7. Analyze Images")
    print("8. Analyze Page Speed")
    print("9. Analyze Schema Markup")
    print("10. Analyze Readability")
    print("11. Analyze Broken Links")
    print("12. Run Full SEO Check")
    print("13. Generate JSON Report")
    print("14. Exit")

    choice = input("Enter your choice (0-14): ")
    return choice

def set_target_url():
    url = input("Enter the URL to analyze: ").strip()
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "http://" + url
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        print("Invalid URL. Please try again.")
        return set_target_url()
    return url

def validate_url(url):
    try:
        headers = {'User-Agent': random_user_agent()}
        response = requests.head(url, allow_redirects=True, headers=headers)
        random_delay()
        print(f"Validated URL: {url} - Status Code: {response.status_code}")
        return response.status_code == 200
    except RequestException as e:
        print(f"Error validating URL: {e}")
        return False

def run_analysis(url, choice):
    global full_report  

    if not url:
        print("No target URL set. Please set a target URL first.")
        return None

    if not validate_url(url):
        print("The URL is invalid or unreachable. Please set a valid URL.")
        return None

    print(f"Running analysis for choice: {choice}")
    
    try:
        if choice == '1':
            analyzer = MetaInformationAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '2':
            analyzer = PageQualityAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '3':
            analyzer = PageStructureAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '4':
            analyzer = LinkStructureAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '5':
            analyzer = ServerConfigurationAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '6':
            analyzer = ExternalFactorsAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '7':
            analyzer = ImageAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '8':
            analyzer = PageSpeedAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '9':
            analyzer = SchemaMarkupAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '10':
            analyzer = ReadabilityAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '11':
            analyzer = BrokenLinksAnalyzer(url)
            full_report = analyzer.get_analysis_report()
        elif choice == '12':
            print("Performing full SEO check...")
            analyzer = SEOScoreCalculator(url)
            full_report = analyzer.generate_report()
            print(f"Full SEO check completed. Report generated: {full_report}")
        elif choice == '13':
            if not full_report:
                print("No data available to generate a report. Please run a full SEO check first.")
                return None
            save_json_report(full_report)
        elif choice == '14':
            print("Exiting the tool. Goodbye!")
            sys.exit(0)
        elif choice == '0':
            url = set_target_url()
            print(f"Target URL changed to: {url}")
            return None
        else:
            print("Invalid choice. Please try again.")
            return None

        if full_report:
            print_results(full_report)
  
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

def save_json_report(data):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)  
    json_filename = os.path.join(output_dir, "seo_report.json")
    try:
        with open(json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON report saved: {json_filename}")
    except Exception as e:
        print(f"An error occurred while saving the JSON report: {e}")

def print_results(report):
    print("\n--- Analysis Results ---")
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    display_banner()
    target_url = set_target_url()

    while True:
        choice = main_menu()
        run_analysis(target_url, choice)

