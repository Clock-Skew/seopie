import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

class PageStructureAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_h1_heading(self):
        h1_tags = self.soup.find_all('h1')
        h1_count = len(h1_tags)
        recommendations = []

        if h1_count == 0:
            recommendations.append("No H1 heading found. Add an H1 heading to the page.")
        elif h1_count > 1:
            recommendations.append("Multiple H1 headings found. Ensure there is only one H1 heading on the page.")

        return h1_count, recommendations

    def analyze_heading_levels(self):
        headings = self.soup.find_all(re.compile('^h[1-6]$'))
        heading_levels = [heading.name for heading in headings]
        level_counter = Counter(heading_levels)
        recommendations = []

        if not 'h1' in level_counter:
            recommendations.append("No H1 heading found. Add an H1 heading to establish the main topic.")

        for level in range(2, 7):
            if f'h{level-1}' not in level_counter and f'h{level}' in level_counter:
                recommendations.append(f"Missing H{level-1} heading level before H{level}. Ensure proper heading hierarchy.")

        return level_counter, recommendations

    def check_duplicate_headings(self):
        headings = self.soup.find_all(re.compile('^h[1-6]$'))
        heading_texts = [heading.get_text().strip() for heading in headings]
        duplicate_count = sum(count for count in Counter(heading_texts).values() if count > 1)
        recommendations = []

        if duplicate_count > 0:
            recommendations.append("Duplicate headings found. Ensure each heading is unique.")

        return duplicate_count, recommendations

    def evaluate_overall_heading_structure(self):
        headings = self.soup.find_all(re.compile('^h[1-6]$'))
        heading_structure = [(heading.name, heading.get_text().strip()) for heading in headings]
        recommendations = []

        if not any(heading for heading in headings if heading.name == 'h1'):
            recommendations.append("No H1 heading found. Add an H1 heading to establish the main topic.")

        return heading_structure, recommendations

    def get_analysis_report(self):
        report = {
            "H1 Heading": self.analyze_h1_heading(),
            "Heading Levels": self.analyze_heading_levels(),
            "Duplicate Headings": self.check_duplicate_headings(),
            "Overall Heading Structure": self.evaluate_overall_heading_structure()
        }
        return report

