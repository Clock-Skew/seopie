import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

class PageQualityAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_word_count(self):
        text = self.soup.get_text()
        words = re.findall(r'\w+', text)
        word_count = len(words)
        recommendations = []

        if word_count < 300:
            recommendations.append("The page content is too short, consider adding more relevant content.")

        return word_count, recommendations

    def analyze_stop_words(self):
        text = self.soup.get_text()
        words = re.findall(r'\w+', text)
        stop_words = set(["a", "and", "the", "is", "in", "at", "of", "on", "for", "with", "as", "by", "to"])
        stop_word_count = sum(1 for word in words if word.lower() in stop_words)
        total_words = len(words)
        stop_word_percentage = (stop_word_count / total_words) * 100 if total_words > 0 else 0
        recommendations = []

        if stop_word_percentage > 25:
            recommendations.append("The content has too many stop words, consider revising the text.")

        return stop_word_percentage, recommendations

    def analyze_paragraph_usage(self):
        paragraphs = self.soup.find_all('p')
        paragraph_count = len(paragraphs)
        recommendations = []

        if paragraph_count < 3:
            recommendations.append("The content has too few paragraphs, consider dividing the text into more paragraphs.")

        return paragraph_count, recommendations

    def check_placeholder_texts(self):
        text = self.soup.get_text()
        placeholders = ["lorem ipsum", "placeholder text", "sample text"]
        found_placeholders = [placeholder for placeholder in placeholders if placeholder in text.lower()]
        recommendations = []

        if found_placeholders:
            recommendations.append("The content contains placeholder text, consider replacing it with actual content.")

        return found_placeholders, recommendations

    def check_duplicate_content(self):
        paragraphs = self.soup.find_all('p')
        texts = [p.get_text().strip() for p in paragraphs]
        duplicate_count = sum(count for count in Counter(texts).values() if count > 1)
        recommendations = []

        if duplicate_count > 0:
            recommendations.append("The content contains duplicate text, consider removing or rephrasing duplicate content.")

        return duplicate_count, recommendations

    def analyze_mobile_optimization(self):
        meta_viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        viewport_content = meta_viewport['content'] if meta_viewport else 'No viewport meta tag found'
        recommendations = []

        if 'width=device-width' not in viewport_content:
            recommendations.append("The viewport meta tag is missing or incorrect. Add 'width=device-width' for better mobile optimization.")

        return viewport_content, recommendations

    def analyze_social_sharing_widgets(self):
        social_widgets = ["facebook.com", "twitter.com", "linkedin.com", "pinterest.com"]
        found_widgets = [widget for widget in social_widgets if widget in self.soup.prettify()]
        recommendations = []

        if not found_widgets:
            recommendations.append("No social sharing widgets found. Consider adding social sharing buttons to increase engagement.")

        return found_widgets, recommendations

    def get_analysis_report(self):
        report = {
            "Word Count": self.analyze_word_count(),
            "Stop Words": self.analyze_stop_words(),
            "Paragraph Usage": self.analyze_paragraph_usage(),
            "Placeholder Texts": self.check_placeholder_texts(),
            "Duplicate Content": self.check_duplicate_content(),
            "Mobile Optimization": self.analyze_mobile_optimization(),
            "Social Sharing Widgets": self.analyze_social_sharing_widgets()
        }
        return report

