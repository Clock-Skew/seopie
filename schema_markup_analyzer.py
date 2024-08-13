# schema_markup_analyzer.py

import requests
from bs4 import BeautifulSoup

class SchemaMarkupAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_schema_markup(self):
        schema_tags = self.soup.find_all(attrs={"type": "application/ld+json"})
        total_schema_tags = len(schema_tags)
        recommendations = []

        if total_schema_tags == 0:
            recommendations.append("No schema markup found. Add structured data to improve SEO.")

        return {
            "Total Schema Markup Tags": total_schema_tags
        }, recommendations

    def get_analysis_report(self):
        return self.analyze_schema_markup()
