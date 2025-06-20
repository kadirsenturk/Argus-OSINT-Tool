import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import os
import csv

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

console = Console()

def get_scraper(site_name):
    """Returns the scraper function for a given site name if it exists."""
    scrapers = {
        "GitHub": scrape_github,
        "Reddit": scrape_reddit,
        "HackerNews": scrape_hackernews,
        "GitLab": scrape_gitlab,
        "Twitch": scrape_twitch,
        "Steam": scrape_steam,
        "MyAnimeList": scrape_myanimelist,
    }
    return scrapers.get(site_name)

def scrape_github(soup):
    """Scrapes additional information from a GitHub profile page."""
    try:
        name_tag = soup.find('span', class_='p-name')
        if name_tag:
            return f"Name: {name_tag.text.strip()}"
        return "Details not found."
    except Exception:
        return "Scraping error"

def scrape_reddit(soup):
    """Scapes additional information from a Reddit profile page."""
    try:
        script_tag = soup.find('script', id='data')
        if script_tag:
            data = json.loads(script_tag.string)
            user_info = data['user']['redditors'][list(data['user']['redditors'].keys())[0]]
            karma = user_info.get('totalKarma', 0)
            return f"Total Karma: {karma}"
        return "Embedded JSON not found."
    except (KeyError, IndexError, json.JSONDecodeError):
        return "Could not retrieve Karma information."

def scrape_gitlab(soup):
    """Scrapes additional information from a GitLab profile page."""
    try:
        name_tag = soup.find('h1')
        if name_tag:
            return f"Name: {name_tag.text.strip()}"
        return "Details not found."
    except Exception:
        return "Scraping error"

def scrape_hackernews(soup):
    """Scrapes additional information from a Hacker News profile page."""
    try:
        details = []
        karma_tag = soup.find('td', string='karma:')
        if karma_tag and karma_tag.find_next_sibling('td'):
            details.append(f"Karma: {karma_tag.find_next_sibling('td').text.strip()}")
        created_tag = soup.find('td', string='created:')
        if created_tag and created_tag.find_next_sibling('td'):
            details.append(f"Created: {created_tag.find_next_sibling('td').text.strip()}")
        return ", ".join(details) or "Details not found."
    except Exception:
        return "Scraping error"

def scrape_twitch(soup):
    """Scrapes follower count from a Twitch profile page."""
    try:
        # Twitch is very dynamic, so selectors might be complex or change.
        # This targets a paragraph tag that is likely to contain the follower count.
        # A more robust selector might use a `data-test-selector` if available.
        follower_p = soup.find('p', string=lambda t: t and "followers" in t.lower())
        if follower_p:
            # The count is often in a preceding sibling element
            count_span = follower_p.find_previous_sibling('p')
            if count_span and count_span.find('span'):
                 return f"Followers: {count_span.find('span').text.strip()}"
            # Fallback for a different structure
            strong_tag = follower_p.find('strong')
            if strong_tag:
                return f"Followers: {strong_tag.text.strip()}"
        
        # Fallback to a more generic search for a count near the word "followers"
        follower_count_tag = soup.select_one('p.tw-font-size-5.tw-strong')
        if follower_count_tag:
            return f"Followers: {follower_count_tag.text.strip()}"

        return "Follower count not found."
    except Exception:
        return "Scraping error"

def scrape_steam(soup):
    """Scrapes user level and real name from a Steam profile page."""
    try:
        details = []
        level_span = soup.select_one('.friendPlayerLevelNum')
        if level_span:
            details.append(f"Level: {level_span.text.strip()}")
        
        real_name_div = soup.select_one('.actual_persona_name')
        if real_name_div:
            # Steam often puts the real name in a div below the persona name
            # We need to find the specific container
            name_container = real_name_div.parent.find('div', class_=None, recursive=False)
            if name_container and name_container.text.strip():
                 details.append(f"Real Name: {name_container.text.strip()}")

        return ", ".join(details) or "Details not found."
    except Exception:
        return "Scraping error"

def scrape_myanimelist(soup):
    """Scrapes join date and stats from a MyAnimeList profile."""
    try:
        details = []
        # Find the "Joined" stat
        joined_span = soup.find('span', class_='user-status-title', string='Joined')
        if joined_span:
            joined_date = joined_span.find_next_sibling('span', class_='user-status-data')
            if joined_date:
                details.append(f"Joined: {joined_date.text.strip()}")

        # Find other stats
        stats_container = soup.select_one('div.stats.user-stats')
        if stats_container:
            anime_days = stats_container.select_one('div.stat-score a')
            if anime_days:
                 details.append(f"Anime Days: {anime_days.text.strip()}")
        
        return ", ".join(details) or "Details not found."
    except Exception:
        return "Scraping error"


def check_site(site_name, site_info, username):
    """
    Checks a site for the username. Each thread launches its own Playwright instance.
    """
    url = site_info["url"].replace("{username}", username)
    result = {"site": site_name, "category": site_info.get("category", "N/A"), "url": url, "status": "Not Found", "details": ""}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
            page = context.new_page()
            
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                if response is None or response.status == 404:
                     return None

                content = page.content()
                error_texts = site_info.get("error_check", [])
                
                if isinstance(error_texts, str):
                    error_texts = [error_texts]

                is_error_present = any(re.search(text, content, re.IGNORECASE) for text in error_texts)
                
                if is_error_present:
                    return None

                result["status"] = "Found"
                scraper_func = get_scraper(site_name)
                if scraper_func and site_info.get("scraper", False):
                    soup = BeautifulSoup(content, "lxml")
                    result["details"] = scraper_func(soup)

            except PlaywrightError:
                result["status"] = "Error (Timeout/Navigation)"
                return None
            finally:
                page.close()
                context.close()
                browser.close()

    except Exception:
        result["status"] = "Error (Playwright init)"
        return None

    return result


def run_osint_for_username(username, sites_to_scan):
    """Runs the OSINT scan for a given username across the specified sites."""
    found_accounts = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"[green]Searching...", total=len(sites_to_scan))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_site = {executor.submit(check_site, name, info, username): name for name, info in sites_to_scan.items()}
            
            for future in as_completed(future_to_site):
                res = future.result()
                if res and res["status"] == "Found":
                    found_accounts.append(res)
                progress.update(task, advance=1)

    return sorted(found_accounts, key=lambda x: x['site'])


def save_html_report(query, found_accounts, filename):
    """Saves the found accounts to a modern and stylish HTML file."""
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Argus Report: {query}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f8f9fa; color: #212529; margin: 0; padding: 2rem; }}
            .container {{ width: 100%; max-width: 1000px; margin: auto; background: #fff; padding: 2.5rem; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid #e9ecef; }}
            .header {{ display: flex; align-items: center; gap: 1.5rem; border-bottom: 1px solid #dee2e6; padding-bottom: 1.5rem; margin-bottom: 2rem; }}
            .logo {{ font-size: 3rem; color: #3498db; }}
            .header-text h1 {{ margin: 0; color: #343a40; font-size: 2rem; font-weight: 700; }}
            .header-text p {{ margin: 0; color: #6c757d; font-size: 1rem; }}
            .summary {{ background-color: #e9f5ff; border-left: 5px solid #3498db; padding: 1rem 1.5rem; margin-bottom: 2rem; border-radius: 6px; }}
            .summary p {{ margin: 0; color: #0c5464; }}
            .summary strong {{ font-weight: 600; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 1rem; text-align: left; vertical-align: middle; border-bottom: 1px solid #dee2e6; }}
            th {{ background-color: #f8f9fa; font-weight: 600; color: #495057; }}
            tbody tr:hover {{ background-color: #f1f3f5; }}
            a {{ color: #3498db; text-decoration: none; font-weight: 600; }}
            a:hover {{ text-decoration: underline; }}
            .site-cell {{ display: flex; align-items: center; gap: 0.75rem; }}
            .site-cell img {{ width: 20px; height: 20px; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #dee2e6; font-size: 0.9rem; color: #6c757d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                 <div class="logo">👁️‍🗨️</div>
                 <div class="header-text">
                     <h1>Project Argus</h1>
                     <p>OSINT Report</p>
                 </div>
            </div>
            <div class="summary">
                 <p><strong>Searched Username:</strong> {query}<br>
                 <strong>Accounts Found:</strong> {len(found_accounts)}<br>
                 <strong>Report Date:</strong> {report_time}</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Site</th>
                        <th>Category</th>
                        <th>Found URL</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
    """
    for account in found_accounts:
        domain = re.search(r"https?://(?:www\.)?([^/]+)", account["url"]).group(1)
        favicon_url = f"https://www.google.com/s2/favicons?sz=64&domain_url={domain}"
        html_content += f"""
                    <tr>
                        <td class="site-cell"><img src="{favicon_url}" alt="{account['site']} logo"> {account['site']}</td>
                        <td>{account['category']}</td>
                        <td><a href="{account['url']}" target="_blank">{account['url']}</a></td>
                        <td>{account.get('details', '')}</td>
                    </tr>
        """
    html_content += """
                </tbody>
            </table>
            <div class="footer">
                <p>Generated by Project Argus.</p>
            </div>
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    console.print(f"\n[bold green]✓ HTML Report successfully saved to '{filename}'.[/bold green]")


def save_json_report(query, found_accounts, filename):
    """Saves the found accounts to a JSON file."""
    report = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": found_accounts
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    console.print(f"\n[bold green]✓ JSON Report successfully saved to '{filename}'.[/bold green]")


def save_csv_report(query, found_accounts, filename):
    """Saves the found accounts to a CSV file."""
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "category", "url", "details"])
        for account in found_accounts:
            writer.writerow([account["site"], account["category"], account["url"], account.get("details", "")])
    console.print(f"\n[bold green]✓ CSV Report successfully saved to '{filename}'.[/bold green]")


def main():
    """Main entry point of the program."""
    parser = argparse.ArgumentParser(
        description="Project Argus: An OSINT tool to search for a specified username across various platforms.",
        epilog="Example: python argus.py username -o report.html"
    )
    parser.add_argument("username", help="The username to search for.")
    parser.add_argument("-s", "--site", help="Limit the search to a single specified site (e.g., GitHub).")
    parser.add_argument("-c", "--category", help="Limit the search to a specific category (e.g., Coding).")
    parser.add_argument("-o", "--output", help="Save the results to the specified file (html, json, csv).")
    args = parser.parse_args()

    try:
        with open("sites.json", "r", encoding="utf-8") as f:
            all_sites = json.load(f)
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] 'sites.json' file not found.")
        return
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] 'sites.json' file is not formatted correctly.")
        return

    sites_to_scan = {}
    title_category = "All"

    if args.site:
        site_name_lower = args.site.lower()
        for name, info in all_sites.items():
            if name.lower() == site_name_lower:
                sites_to_scan = {name: info}
                title_category = name
                break
        if not sites_to_scan:
            console.print(f"[bold red]Error:[/bold red] Site named '{args.site}' not found.")
            return
    elif args.category:
        category_lower = args.category.lower()
        sites_to_scan = {name: info for name, info in all_sites.items() if info.get("category", "").lower() == category_lower}
        title_category = args.category
        if not sites_to_scan:
            console.print(f"[bold red]Error:[/bold red] No sites found in category '{args.category}'.")
            return
    else:
        sites_to_scan = all_sites

    search_message = f"Searching for [bold cyan]'{args.username}'[/bold cyan] on [bold yellow]{len(sites_to_scan)}[/bold yellow] sites..."
    if title_category != "All":
        search_message += f" (Filter: [bold green]{title_category}[/bold green])"
    console.print(search_message)
    
    found_accounts = run_osint_for_username(args.username, sites_to_scan)

    if found_accounts:
        console.print(f"\n[bold]Search finished. Found [green]{len(found_accounts)}[/green] account(s) in total.[/bold]")
        table = Table(title=f"Search Results")
        table.add_column("Site", style="cyan", width=15)
        table.add_column("Category", style="magenta", width=15)
        table.add_column("Found URL", style="green")
        table.add_column("Details", style="yellow")
        
        for account in found_accounts:
            table.add_row(account["site"], account["category"], f"[link={account['url']}]{account['url']}[/link]", account.get("details", ""))
        
        console.print(table)

        if args.output:
            if args.output.endswith(".html"):
                save_html_report(args.username, found_accounts, args.output)
            elif args.output.endswith(".json"):
                save_json_report(args.username, found_accounts, args.output)
            elif args.output.endswith(".csv"):
                save_csv_report(args.username, found_accounts, args.output)
            else:
                console.print(f"[bold red]Error:[/bold red] Unsupported report format. Please use .html, .json, or .csv.")
    else:
        console.print(f"\n[bold red]Search finished. No accounts found for '{args.username}'.[/bold red]")


if __name__ == "__main__":
    main()