import requests

class ServerConfigurationAnalyzer:
    def __init__(self, url):
        self.url = url
        self.response = self.get_response()

    def get_response(self):
        return requests.get(self.url)

    def analyze_http_headers(self):
        headers = self.response.headers
        recommendations = []

        if 'Server' in headers:
            recommendations.append("The web server version is sent within the HTTP header. Consider hiding the server version for security reasons.")

        if 'X-Powered-By' in headers:
            recommendations.append("The X-Powered-By HTTP header is sent. Consider removing it for security reasons.")

        if 'Content-Encoding' not in headers or headers['Content-Encoding'] != 'gzip':
            recommendations.append("The page does not use GZip for compressed data transmission. Enable GZip compression to reduce the page size and improve performance.")

        return headers, recommendations

    def analyze_http_redirects(self):
        response = requests.head(self.url, allow_redirects=True)
        redirects = response.history
        recommendations = []

        if redirects:
            for i, redirect in enumerate(redirects):
                if not redirect.is_permanent_redirect:
                    recommendations.append(f"HTTP redirect {i+1} is not permanent. Use permanent redirects (301) instead of temporary redirects (302).")

        return redirects, recommendations

    def evaluate_server_performance(self):
        server_performance = {
            'status_code': self.response.status_code,
            'content_length': len(self.response.content),
            'response_time': self.response.elapsed.total_seconds()
        }
        recommendations = []

        if server_performance['response_time'] > 0.4:
            recommendations.append("The page response time is longer than the recommended limit of 0.4 seconds. Optimize server performance to reduce response time.")

        if server_performance['content_length'] > 500000:
            recommendations.append("The file size of the HTML document is very large. Reduce the file size to improve performance.")

        return server_performance, recommendations

    def measure_response_times(self):
        times = []
        for _ in range(5):
            response = requests.get(self.url)
            times.append(response.elapsed.total_seconds())
        average_response_time = sum(times) / len(times)
        recommendations = []

        if average_response_time > 0.4:
            recommendations.append("The average response time is longer than the recommended limit of 0.4 seconds. Optimize server performance to reduce response time.")

        return average_response_time, recommendations

    def get_analysis_report(self):
        report = {
            "HTTP Headers": self.analyze_http_headers(),
            "HTTP Redirects": self.analyze_http_redirects(),
            "Server Performance": self.evaluate_server_performance(),
            "Response Times": self.measure_response_times()
        }
        return report

