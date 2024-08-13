from meta_information_analyzer import MetaInformationAnalyzer
from page_quality_analyzer import PageQualityAnalyzer
from page_structure_analyzer import PageStructureAnalyzer
from link_structure_analyzer import LinkStructureAnalyzer
from server_configuration_analyzer import ServerConfigurationAnalyzer
from external_factors_analyzer import ExternalFactorsAnalyzer

class SEOScoreCalculator:
    def __init__(self, url, ignore_robots=False):
        self.url = url
        self.ignore_robots = ignore_robots
        self.meta_analyzer = MetaInformationAnalyzer(url)
        self.page_quality_analyzer = PageQualityAnalyzer(url)
        self.page_structure_analyzer = PageStructureAnalyzer(url)
        self.link_structure_analyzer = LinkStructureAnalyzer(url)
        self.server_configuration_analyzer = ServerConfigurationAnalyzer(url)
        self.external_factors_analyzer = ExternalFactorsAnalyzer(url)  # No API key needed 
        self.analysis_results = self.get_all_analysis_results()

    def get_all_analysis_results(self):
        results = {
            "Meta Information": self.meta_analyzer.get_analysis_report(),
            "Page Quality": self.page_quality_analyzer.get_analysis_report(),
            "Page Structure": self.page_structure_analyzer.get_analysis_report(),
            "Link Structure": self.link_structure_analyzer.get_analysis_report(),
            "Server Configuration": self.server_configuration_analyzer.get_analysis_report(),
            "External Factors": self.external_factors_analyzer.get_analysis_report(),
        }
        return results

    def calculate_score(self):
        # Define weights for each category
        weights = {
            "Meta Information": 0.2,
            "Page Quality": 0.2,
            "Page Structure": 0.2,
            "Link Structure": 0.2,
            "Server Configuration": 0.1,
            "External Factors": 0.1,
        }

        total_score = 0
        for category, result in self.analysis_results.items():
            score = self.calculate_category_score(result)
            total_score += score * weights[category]

        return round(total_score * 100, 2)

    def calculate_category_score(self, category_result):
        score = 1.0
        for key, value in category_result.items():
            if isinstance(value, tuple):
                recommendations = value[-1]
                if recommendations:
                    score -= 0.1 * len(recommendations)
        return max(score, 0)

    def generate_report(self):
        score = self.calculate_score()
        report = {
            "Overall SEO Score": score,
            "Detailed Analysis": self.analysis_results
        }
        return report

