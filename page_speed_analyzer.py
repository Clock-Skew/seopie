# page_speed_analyzer.py

import requests
import time

class PageSpeedAnalyzer:
    def __init__(self, url):
        self.url = url

    def analyze_page_speed(self):
        start_time = time.time()
        response = requests.get(self.url)
        load_time = time.time() - start_time
        recommendations = []

        if load_time > 3:
            recommendations.append(f"Page load time is {load_time:.2f} seconds, which is above the recommended limit of 3 seconds. Consider optimizing images, scripts, and server performance.")

        return {
            "Page Load Time (seconds)": load_time
        }, recommendations

    def get_analysis_report(self):
        return self.analyze_page_speed()
