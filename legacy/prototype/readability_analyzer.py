# readability_analyzer.py

import requests
from bs4 import BeautifulSoup
import textstat

class ReadabilityAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_readability(self):
        text = self.soup.get_text()
        readability_score = textstat.flesch_reading_ease(text)
        recommendations = []

        if readability_score < 60:
            recommendations.append(f"Readability score is {readability_score:.2f}, which is below the recommended level. Consider simplifying the text for better readability.")

        return {
            "Readability Score": readability_score
        }, recommendations

    def get_analysis_report(self):
        return self.analyze_readability()
