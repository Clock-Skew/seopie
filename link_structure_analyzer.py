import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from collections import Counter  # Add this import

class LinkStructureAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()
        self.base_url = urlparse(url).scheme + "://" + urlparse(url).netloc

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_internal_links(self):
        links = self.soup.find_all('a', href=True)
        internal_links = [link['href'] for link in links if self.is_internal_link(link['href'])]
        recommendations = []

        if len(internal_links) < 1:
            recommendations.append("No internal links found. Add internal links to improve navigation and SEO.")

        return internal_links, recommendations

    def is_internal_link(self, href):
        return href.startswith('/') or self.base_url in href

    def analyze_external_links(self):
        links = self.soup.find_all('a', href=True)
        external_links = [link['href'] for link in links if not self.is_internal_link(link['href'])]
        recommendations = []

        if len(external_links) > 50:
            recommendations.append("Too many external links found. Reduce the number of external links to avoid link dilution.")

        return external_links, recommendations

    def check_dynamic_parameters(self):
        links = self.soup.find_all('a', href=True)
        dynamic_links = [link['href'] for link in links if '?' in link['href'] and not link['href'].startswith('#')]
        recommendations = []

        if dynamic_links:
            recommendations.append("Dynamic parameters found in internal links. Use static URLs where possible.")

        return dynamic_links, recommendations

    def evaluate_anchor_texts(self):
        links = self.soup.find_all('a', href=True)
        anchor_texts = [link.get_text().strip() for link in links]
        duplicate_texts = [text for text, count in Counter(anchor_texts).items() if count > 1]
        recommendations = []

        if duplicate_texts:
            recommendations.append("Duplicate anchor texts found. Ensure each anchor text is unique and descriptive.")

        return duplicate_texts, recommendations

    def count_links(self):
        links = self.soup.find_all('a', href=True)
        total_links = len(links)
        internal_links = len([link for link in links if self.is_internal_link(link['href'])])
        external_links = total_links - internal_links
        recommendations = []

        if total_links < 50:
            recommendations.append("Too few links found. Add more relevant links to improve site navigation and SEO.")

        return total_links, internal_links, external_links, recommendations

    def get_analysis_report(self):
        report = {
            "Internal Links": self.analyze_internal_links(),
            "External Links": self.analyze_external_links(),
            "Dynamic Parameters": self.check_dynamic_parameters(),
            "Anchor Texts": self.evaluate_anchor_texts(),
            "Link Counts": self.count_links()
        }
        return report

