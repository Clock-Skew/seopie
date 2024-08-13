# broken_links_analyzer.py

import requests
from bs4 import BeautifulSoup

class BrokenLinksAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_broken_links(self):
        links = self.soup.find_all('a', href=True)
        broken_links = []
        recommendations = []

        for link in links:
            href = link['href']
            if href.startswith('http') and not self.is_link_working(href):
                broken_links.append(href)

        if broken_links:
            recommendations.append(f"Found {len(broken_links)} broken links. Fix or remove these links.")

        return {
            "Total Links": len(links),
            "Broken Links": len(broken_links)
        }, recommendations

    def is_link_working(self, url):
        try:
            response = requests.head(url)
            return response.status_code == 200
        except:
            return False

    def get_analysis_report(self):
        return self.analyze_broken_links()
