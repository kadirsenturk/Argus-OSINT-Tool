# Project ArgusEye 👁️‍🗨️

Project ArgusEye is an advanced OSINT (Open Source Intelligence) tool developed to search for a specific username across various websites and report on the findings. It presents the results both on the command line and in a modern HTML report.

![Report Sample](https://i.imgur.com/GjT8l0R.png)

## Features

-   Searches for usernames on over 70 popular websites.
-   Easily add or edit sites via the `sites.json` file.
-   Displays results in a clean, colorized table in the terminal using `rich`.
-   Generates a modern and stylish HTML report for found accounts (`-o` flag).
-   High accuracy on JavaScript-heavy sites thanks to Playwright.
-   `error_check` mechanism to minimize false positives by checking for "user not found" messages.
-   **Multi-language support:** Both the command-line interface and reports are available in English and Turkish.

## Installation

Python 3.8 or higher is required to run the project.

**1. Clone the Repository:**
```bash
git clone <repository_url>
cd Project-ArgusEye 
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

**Basic Search (in English):**
```bash
python argus.py <username>
```
Example: `python argus.py aydinpy`

**Generating an HTML Report:**
Use the `-o` or `--output` flag to create an HTML report for the found accounts.
```bash
python argus.py <username> -o
```
This command will create a file named `report_<username>.html`.

**Generating a CSV Report:**
Use the `-c` or `--csv` flag to create a CSV report.
```bash
python argus.py <username> -c
```
This command will create a file named `report_<username>.csv`.

### Language Selection

The tool supports English (`en`) and Turkish (`tr`). The default language is English. Use the `--lang` flag to select a different language for both the interface and the reports.

**Running a search in Turkish:**
```bash
python argus.py <username> --lang tr
```

**Getting help in Turkish:**
```bash
python argus.py --help --lang tr
```

### All Arguments
```
usage: argus.py [-h] [-o] [-c] [--lang {en,tr}] query

Project ArgusEye: An advanced OSINT tool for username reconnaissance.

positional arguments:
  query                 The username to search for.

options:
  -h, --help            show this help message and exit
  -o, --output          Generate an HTML report for the found accounts.
  -c, --csv             Generate a CSV report for the found accounts.
  --lang {en,tr}        Select the application and report language (en/tr).
                        Default: en
```

## Configuration (`sites.json`)

The heart of the project is the `sites.json` file. This file defines which sites the program will search and how it will interact with them.

-   **Adding/Removing Sites:** You can edit this file to add a new site or remove an existing one.
-   **Enabling/Disabling Scrapers:**
    -   `"scraper": true`: The program will attempt to scrape profile information for this site. This requires a corresponding `scrape_...` function in `argus.py`.
    -   `"scraper": false`: The program only checks for the existence of the username, which is useful for sites with bot protection or for which a scraper has not yet been written.
-   **Error Checking:** The `"error_check"` field contains a list of strings that appear on "user not found" pages. This is crucial for preventing false positives.
-   **Notes:** The `"note"` field can be used to add reminders about a site.

### `sites.json` Example Structure
```json
{
  "GitHub": {
    "url": "https://www.github.com/{}",
    "category": "Programming",
    "scraper": true,
    "note": "Profile page",
    "error_check": ["Not Found"]
  },
  "DeviantArt": {
    "url": "https://www.deviantart.com/{}",
    "category": "Design",
    "scraper": false,
    "note": "Scraper disabled due to the site's dynamic structure.",
    "error_check": ["Page Not Found"]
  }
}
``` 