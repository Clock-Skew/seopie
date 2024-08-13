# image_analyzer.py

import requests
from bs4 import BeautifulSoup

class ImageAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_images(self):
        images = self.soup.find_all('img')
        total_images = len(images)
        images_without_alt = [img for img in images if not img.get('alt')]
        recommendations = []

        if images_without_alt:
            recommendations.append(f"{len(images_without_alt)} images are missing alt attributes. Add descriptive alt text to all images.")

        return {
            "Total Images": total_images,
            "Images Without Alt": len(images_without_alt)
        }, recommendations

    def get_analysis_report(self):
        return self.analyze_images()
