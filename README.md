<div align="center">
  <br />
  <p>
    <a href="https://github.com/kadirsenturk/Argus-OSINT-Tool"><img src="assets/logo.svg" alt="Argus Logo" width="150" /></a>
  </p>
  <h1 align="center"><b>Project Argus</b></h1>
  <p align="center">
    An advanced OSINT tool for username reconnaissance across a multitude of websites.
    <br />
    <a href="https://github.com/kadirsenturk/Argus-OSINT-Tool/issues/new?template=bug_report.md">Report Bug</a>
    ·
    <a href="https://github.com/kadirsenturk/Argus-OSINT-Tool/issues/new?template=feature_request.md">Request Feature</a>
  </p>

  <p align="center">
    <a href="/LICENSE"><img src="https://img.shields.io/github/license/kadirsenturk/Argus-OSINT-Tool?style=for-the-badge" alt="license"></a>
    <a href="https://github.com/kadirsenturk/Argus-OSINT-Tool/stargazers"><img src="https://img.shields.io/github/stars/kadirsenturk/Argus-OSINT-Tool?style=for-the-badge" alt="stars"></a>
    <a href="https://github.com/kadirsenturk/Argus-OSINT-Tool/issues"><img src="https://img.shields.io/github/issues/kadirsenturk/Argus-OSINT-Tool?style=for-the-badge" alt="issues"></a>
  </p>
</div>

---

## 📖 About

**Project Argus** is an advanced OSINT (Open Source Intelligence) tool developed to search for a specific username across various websites and report on the findings. It leverages modern technologies like Playwright to ensure high accuracy on dynamic, JavaScript-heavy sites where traditional tools might fail. The results are presented both on the command line and in a clean, modern HTML report.

## ✨ Features

-   **Wide Reach:** Searches for usernames on over 90 popular websites.
-   **High Accuracy:** Uses Playwright for reliable detection on dynamic, single-page applications (SPAs).
-   **Concurrent Scanning:** Employs a thread pool for fast, concurrent scanning of multiple sites.
-   **Data Scraping:** Includes scrapers for popular sites like GitHub, Twitch, and Steam to fetch additional profile data (e.g., follower counts, karma).
-   **Intelligent Error Handling:** An `error_check` mechanism minimizes false positives by verifying "user not found" messages unique to each site.
-   **Clean Reporting:** Displays results in a colorized table in the terminal (`rich`) and generates a stylish, self-contained HTML report (`-o` flag).
-   **Extensible:** Easily add or edit sites by modifying the `sites.json` file.

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   Git

### ⚙️ Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/kadirsenturk/Argus-OSINT-Tool.git
    cd Argus-OSINT-Tool
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Required Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright Browsers:**
    This one-time command downloads the necessary browser engines for automation.
    ```bash
    playwright install
    ```

### ▶️ Usage

You can perform a username search by running the `argus.py` script from the command line.

-   **Basic Search:**
    ```bash
    python argus.py <username>
    ```
    *Example:* `python argus.py aydinpy`

-   **Generating an HTML Report:**
    Use the `-o` or `--output` flag to create an HTML report. The report will be saved as `report_<username>.html` in the same directory.
    ```bash
    python argus.py <username> -o
    ```

### 📋 All Arguments
```
usage: argus.py [-h] [-o] query

Project Argus: An advanced OSINT tool for username reconnaissance.

positional arguments:
  query       The username to search for.

options:
  -h, --help  show this help message and exit
  -o, --output Generate an HTML report for the found accounts.
```

## 🔧 Configuration (`sites.json`)

The core of the project is the `sites.json` file, which defines the websites to be scanned.

-   **Adding/Removing Sites:** You can edit this file to add a new site or remove an existing one.
-   **Enabling/Disabling Scrapers:**
    -   `"scraper": true`: Argus will attempt to scrape profile information. This requires a corresponding `scrape_...` function in `argus.py`.
    -   `"scraper": false`: Argus only checks for the existence of the username. Ideal for sites with strong bot protection.
-   **Error Checking:** The `"error_check"` field contains strings that appear on "user not found" pages. This is crucial for accuracy.
-   **URL Formatting:** Use `{username}` as the placeholder for the username in the site's URL.

#### `sites.json` Example
```json
{
  "GitHub": {
    "url": "https://www.github.com/{username}",
    "category": "Coding",
    "scraper": true,
    "note": "Profile page",
    "error_check": "Not Found"
  },
  "DeviantArt": {
    "url": "https://www.deviantart.com/{username}",
    "category": "Design",
    "scraper": false,
    "note": "Scraper disabled due to dynamic site structure.",
    "error_check": "Page not found"
  }
}
```

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

-   **Playwright:** For the powerful browser automation that makes high-accuracy checking possible.
-   **Rich:** For beautiful and informative terminal output.
