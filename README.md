# Project Argus 👁️‍🗨️

Project Argus is an advanced OSINT (Open Source Intelligence) tool developed to search for a specific username across various websites and report on the findings. It presents the results both on the command line and in a modern HTML report.

## Report Sample (HTML)
A clean, modern HTML report is generated for each scan, showing all found accounts categorized by their area (e.g., Coding, Social Media, Gaming).

```
Argus Report for: example_user
=================================

Found Accounts (Total: 3)
---------------------------------

[+] Coding
    - GitHub: https://github.com/example_user (Followers: 123)

[+] Forum
    - HackerNews: https://news.ycombinator.com/user?id=example_user (Karma: 456)

[+] Gaming
    - Steam: https://steamcommunity.com/id/example_user (Level: 78)
```


## Features

-   Searches for usernames on over 90 popular websites.
-   Easily add or edit sites via the `sites.json` file.
-   Displays results in a clean, colorized table in the terminal using `rich`.
-   Generates a modern and stylish HTML report for found accounts (`-o` or `--output` flag).
-   High accuracy on JavaScript-heavy sites thanks to Playwright and concurrent processing.
-   `error_check` mechanism to minimize false positives by checking for "user not found" messages.
-   Built-in data scrapers for popular sites like GitHub, Twitch, Steam, and more to fetch extra profile data.

## Installation

Python 3.8 or higher is required to run the project.

**1. Clone the Repository:**
```bash
git clone https://github.com/kadirsenturk/Argus-OSINT-Tool.git
cd Argus-OSINT-Tool
```

**2. Create and Activate a Virtual Environment (Recommended):**
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Required Libraries:**
```bash
pip install -r requirements.txt
```

**4. Install Playwright Browsers:**
This command will download the necessary browser engines (Chromium, Firefox, WebKit) for automation.
```bash
playwright install
```

## Usage

You can perform a username search by running the `argus.py` script from the command line.

**Basic Search:**
```bash
python argus.py <username>
```
*Example:* `python argus.py aydinpy`

**Generating an HTML Report:**
Use the `-o` or `--output` flag to create an HTML report for the found accounts. The report will be saved in the same directory.
```bash
python argus.py <username> -o
```
This command will create a file named `report_<username>.html`.


### All Arguments
```
usage: argus.py [-h] [-o] query

Project Argus: An advanced OSINT tool for username reconnaissance.

positional arguments:
  query       The username to search for.

options:
  -h, --help  show this help message and exit
  -o, --output Generate an HTML report for the found accounts.
```

## Configuration (`sites.json`)

The heart of the project is the `sites.json` file. This file defines which sites the program will search and how it will interact with them.

-   **Adding/Removing Sites:** You can edit this file to add a new site or remove an existing one.
-   **Enabling/Disabling Scrapers:**
    -   `"scraper": true`: The program will attempt to scrape profile information for this site. This requires a corresponding `scrape_...` function in `argus.py`.
    -   `"scraper": false`: The program only checks for the existence of the username. This is useful for sites with strong bot protection or for which a scraper has not yet been written.
-   **Error Checking:** The `"error_check"` field contains a list of strings that appear on "user not found" pages. This is crucial for preventing false positives.
-   **URL Formatting:** Use `{username}` as the placeholder for the username in the URL.

### `sites.json` Example Structure
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