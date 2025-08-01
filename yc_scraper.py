import pandas as pd
from playwright.sync_api import sync_playwright
import time


def scrape_yc_ai_companies():
    """
    Scrapes the first 3 AI companies from Y Combinator's website,
    extracts their description and website link from their detail page,
    and saves the data to a CSV file.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True for background execution
        page = browser.new_page()

        # Step 1: Open the website link
        try:
            # The URL now points to the AI industry page directly
            page.goto("https://www.ycombinator.com/companies/industry/ai", timeout=60000)
            print("✅ Successfully navigated to the AI companies page.")
        except Exception as e:
            print(f"❌ Error navigating to the website: {e}")
            browser.close()
            return

        # Wait for the company list to be visible
        try:
            # We wait for the new, more specific selector to appear
            page.wait_for_selector('a.shrink-0[href^="/companies/"]', timeout=30000)
            print("✅ Company list is visible.")
        except Exception as e:
            print(f"❌ Error waiting for the company list: {e}")
            browser.close()
            return

        # Get the href attributes for the first 3 companies
        # MODIFIED: Using a more specific selector based on your reference HTML
        # This locator now looks for an 'a' tag with the class 'shrink-0' AND an href starting with '/companies/'
        company_links = page.locator('a.shrink-0[href^="/companies/"]').all()

        company_urls = [link.get_attribute('href') for link in company_links[:100]]

        print(f"Found URLs for the first 3 companies: {company_urls}")

        scraped_data = []

        # ---
        # Step 2 & 3: Navigate to each company page and scrape the details
        # ---
        for i, url in enumerate(company_urls):
            if not url:
                continue

            full_url = f"https://www.ycombinator.com{url}"
            print(f"\n⚙️ Navigating to company {i + 1}: {full_url}")
            try:
                page.goto(full_url, timeout=60000)

                # Wait for a key element on the detail page to ensure it's loaded
                page.wait_for_selector('h1', timeout=30000)

                # Scrape the company name from the H1 tag (still useful for the CSV)
                company_name = page.locator('h1').inner_text()

                # --- MODIFIED LOCATORS BASED ON YOUR HTML ---

                # Scrape the Description using the new, specific locator
                description_element = page.locator('div.prose.whitespace-pre-line').first
                description = description_element.inner_text().strip() if description_element else "Not found"

                # Scrape the Website Link using the new, specific locator
                # We target the 'a' tag within the div that has the 'text-linkColor' class
                website_link_element = page.locator('div.text-linkColor a').first
                website_link = website_link_element.get_attribute('href') if website_link_element else "Not found"

                visible_page_text = page.locator('body').inner_text()

                print(f"  - Company: {company_name}")
                print(f"  - Description: {' '.join(description.split()[:15])}...")
                print(f"  - Website: {website_link}")
                print(f"  - Captured visible page text (Size: {len(visible_page_text)} characters)")

                scraped_data.append({
                    "Company Name": company_name,
                    "Description": description,
                    "Website Link": website_link,
                    "Visible Page Text": visible_page_text  # Add the new, clean text data
                })

                time.sleep(1)  # A small delay to be respectful to the server

            except Exception as e:
                print(f"❌ Error scraping data for {full_url}: {e}")

        browser.close()

        # Store the data in a CSV file
        if scraped_data:
            df = pd.DataFrame(scraped_data)
            df.to_csv("yc_ai_companies.csv", index=False, encoding='utf-8')
            print("\n✅ Data successfully scraped and saved to yc_ai_companies.csv")
        else:
            print("\n⚠️ No data was scraped.")

if __name__ == "__main__":
        scrape_yc_ai_companies()