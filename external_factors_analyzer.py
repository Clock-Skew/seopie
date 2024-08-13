from urllib.parse import urlparse

class ExternalFactorsAnalyzer:
    def __init__(self, url):
        self.url = url
        self.domain = self.get_domain(url)

    def get_domain(self, url):
        return urlparse(url).netloc

    def analyze_backlinks(self):

        backlinks = {
            "total_backlinks": "N/A",
            "referring_domains": "N/A",
            "unique_ip_addresses": "N/A"
        }
        recommendations = ["Backlink analysis is not available without an API."]
        return backlinks, recommendations

    def analyze_page_authority(self):

        authority = {
            "page_authority": "N/A",
            "domain_authority": "N/A"
        }
        recommendations = ["Page authority analysis is not available without an API."]
        return authority, recommendations

    def get_analysis_report(self):

        report = {
            "Backlinks": self.analyze_backlinks(),
            "Page Authority": self.analyze_page_authority()
        }
        return report

