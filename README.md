# SEO<sub>pie

[![](https://i.ibb.co/MhP1vCP/Picsart-24-08-11-23-53-03-023.png)](https://i.ibb.co/MhP1vCP/Picsart-24-08-11-23-53-03-023.png)

![Static Badge](https://img.shields.io/badge/SEO-pie-yellow?style=for-the-badge) ![Static Badge](https://img.shields.io/badge/Python-blue?style=for-the-badge) ![Static Badge](https://img.shields.io/badge/Site-Eval-white?style=for-the-badge) ![Static Badge](https://img.shields.io/badge/SEO-Audit-yellow?style=for-the-badge) ![Static Badge](https://img.shields.io/badge/Quality-Assessment-black?style=for-the-badge) 


## Overview

SEOpie is a comprehensive Python-based utility designed to analyze various aspects of a website's SEO performance. This tool provides a JSON report detailing the results of the analyses. The overall SEO score calculation is typically a weighted combination of various factors that contribute to a website's search engine optimization. While the exact method of calculating the SEO score can vary depending on the implementation, below is a general overview of how an overall SEO score might be calculated.


------------



#### Meta Information:

- **Title Tag:** Length, relevance, and presence of keywords.

- **Meta Description:** Length, relevance, and keyword usage.

- **Canonical Tags:** Proper use of canonical tags to avoid duplicate content issues.

- **Language and Charset:** Correct setting of language and character set.

#### Content Quality:

- **Word Count:** Optimal word count for the type of content.

- **Keyword Density:** Appropriate use of target keywords.

- **Duplicate Content:** Checks for duplicated text across pages.

- **Mobile Optimization:** Ensurers the content is optimized for mobile devices.

#### Page Structure:

- Heading Structure: Proper use of H1, H2, and other headings.

- Internal Linking: Efficient use of internal links to enhance content structure.

- Broken Links: Identification and correction of broken internal and external links.


------------



### Technical SEO:

**Page Speed:** Performance metrics like loading time, time to first byte, etc.

**Server Configuration:** Correct HTTP status codes, proper use of security headers, etc.

**Schema Markup:** Use of structured data to improve search engine understanding.

### External Factors:

**~~Backlinks:~~** Quality and quantity of backlinks pointing to the site. (Paid 3rd party API Required)

**~~Social Signals~~:** Engagement from social media platforms. (Paid 3rd party API Required)

### Readability:

**Reading Level:** Assessing the complexity of the text using readability scores.

**Clarity:** Ensuring the content is clear and easy to understand for the target audience.

**Navigation:** Ease of navigation and user experience.


------------



#### Scoring The Factors

For each factor, the tool will score the website on a scale (e.g., 0 to 100). For example:

```
Meta Information: 85

Content Quality: 70

Page Structure: 90

Technical SEO: 80

External Factors: 60

Readability: 75

User Experience: 80

Multiply each factor’s score by its weight and sum the results:
Overall SEO Score = 
(85 * 0.20) + (70 * 0.25) + (90 * 0.15) + 
(80 * 0.20) + (60 * 0.10) + (75 * 0.05) + (80 * 0.05)

The weighted scores are summed to get the overall SEO score. For the example above:

Overall SEO Score = 
17 + 17.5 + 13.5 + 16 + 6 + 3.75 + 4 = 77.75

```

Customization: The weightings and factors can be customized based on the priorities of your specific needs. SEO is constantly evolving, so the factors and their importance may change over time.




## Features

- **Meta Information Analysis**: Analyzes meta tags, title, description, canonical URLs, and more.

- **Page Quality Analysis**: Evaluates content quality, word count, stop words, duplicate content, and mobile optimization.

- **Page Structure Analysis**: Checks heading hierarchy, duplicate headings, and overall structure.

- **Link Structure Analysis**: Analyzes internal and external links for SEO compliance.

- **Server Configuration Analysis**: Evaluates server settings, including HTTP headers.

- **~~External Factors Analysis~~**: Checks for external factors that can affect SEO. (Partial (Paid 3rd party API Required)) 

- **Image Analysis**: Analyzes images on the page for SEO best practices.

- **Page Speed Analysis**: Evaluates the page's loading speed and performance.

- **Schema Markup Analysis**: Checks for structured data and schema markup compliance.

- **Readability Analysis**: Assesses the readability of the content.

- **Broken Links Analysis**: Detects broken links on the page.



## Installation

### Prerequisites

- Python 3.x
- pip 

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Clock-Skew/seopie && cd seopie
    ```

2. **Install Required Python Packages**:
    Install the dependencies listed in the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage 

1. **Running the Tool**:
    - Run the script:
    ```bash
    python3 main.py
    ```

### Use Cases

- **SEO Audits**: Use this tool to perform comprehensive SEO audits on websites, identifying areas for improvement.
- **Content Quality Assessment**: Evaluate the readability and overall quality of the website's content.
- **Technical SEO Analysis**: Assess server configurations, page speed, and schema markup to ensure technical compliance.
- **Link Structure Evaluation**: Analyze the internal and external link structure for SEO best practices.

### License

#### MIT License

------------


### Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for any bugs or feature requests.

