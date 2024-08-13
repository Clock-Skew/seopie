import requests
from bs4 import BeautifulSoup

class MetaInformationAnalyzer:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def analyze_title(self):
        title_tag = self.soup.find('title')
        title = title_tag.string if title_tag else 'No title found'
        recommendations = []

        if title:
            if len(title) > 60:
                recommendations.append("Title is too long, consider shortening it.")
            if title.lower().count(title.split()[0].lower()) > 1:
                recommendations.append("Avoid repetition in the title.")
        else:
            recommendations.append("No title found. Add a title to the page.")

        return title, recommendations

    def analyze_meta_description(self):
        meta_description_tag = self.soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description_tag['content'] if meta_description_tag else 'No meta description found'
        recommendations = []

        if meta_description:
            if len(meta_description) > 160:
                recommendations.append("Meta description is too long, consider shortening it.")
        else:
            recommendations.append("No meta description found. Add a meta description to the page.")

        return meta_description, recommendations

    def analyze_canonical_url(self):
        canonical_tag = self.soup.find('link', rel='canonical')
        canonical_url = canonical_tag['href'] if canonical_tag else 'No canonical URL found'
        recommendations = []

        if not canonical_url:
            recommendations.append("No canonical URL found. Add a canonical URL to the page.")

        return canonical_url, recommendations

    def analyze_language(self):
        html_tag = self.soup.find('html')
        language = html_tag.get('lang', 'No language defined') if html_tag else 'No language defined'
        recommendations = []

        if language == 'No language defined':
            recommendations.append("No language attribute found in HTML tag. Define the language in the HTML tag.")

        return language, recommendations

    def analyze_charset(self):
        meta_charset_tag = self.soup.find('meta', attrs={'charset': True})
        charset = meta_charset_tag['charset'] if meta_charset_tag else 'No charset defined'
        recommendations = []

        if charset != 'utf-8':
            recommendations.append("Charset is not set to UTF-8. Set the charset to UTF-8 for better compatibility.")

        return charset, recommendations

    def analyze_other_meta_tags(self):
        meta_tags = self.soup.find_all('meta')
        other_meta_tags = {meta.attrs['name']: meta.attrs['content'] for meta in meta_tags if 'name' in meta.attrs}
        recommendations = []

        if 'robots' not in other_meta_tags:
            recommendations.append("No 'robots' meta tag found. Add a 'robots' meta tag to control search engine behavior.")

        return other_meta_tags, recommendations

    def get_analysis_report(self):
        report = {
            "Title": self.analyze_title(),
            "Meta Description": self.analyze_meta_description(),
            "Canonical URL": self.analyze_canonical_url(),
            "Language": self.analyze_language(),
            "Charset": self.analyze_charset(),
            "Other Meta Tags": self.analyze_other_meta_tags()
        }
        return report

