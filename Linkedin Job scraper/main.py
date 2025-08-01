import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError
import time


def scrape_linkedin_jobs():
    """
    Scrapes job listings for "Software Engineer" from LinkedIn.

    The user is required to manually log in after the browser opens.
    The script then scrolls to load all jobs, scrapes the details for each,
    and saves the data to a CSV file.
    """
    with sync_playwright() as p:
        # Launch browser in non-headless mode to allow for manual login
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Step 1: Navigate to the LinkedIn jobs search page
        search_url = "https://www.linkedin.com/jobs/search/?keywords=Software%20engineer"
        try:
            page.goto(search_url, timeout=60000)
            print("✅ Successfully navigated to the LinkedIn jobs page.")
        except TimeoutError:
            print(f"❌ Error: Timed out while loading {search_url}")
            browser.close()
            return

        # --- MANUAL LOGIN STEP ---
        print("\n" + "=" * 50)
        print("🚨 ACTION REQUIRED: Please log in to your LinkedIn account in the browser window.")
        input("   Press Enter in this terminal after you have successfully logged in...")
        print("=" * 50 + "\n")
        print("Resuming script...")

        # Step 2: Scroll to the bottom of the listings to load all jobs
        print("⚙️ Loading all job listings by scrolling...")
        try:
            job_list_selector = "ul.jobs-search-results__list"
            page.wait_for_selector(job_list_selector, timeout=30000)

            # Get the scrollable element
            scrollable_list = page.locator(job_list_selector)

            # Scroll down until no new jobs are loaded
            last_height = 0
            while True:
                await scrollable_list.evaluate("element => element.scrollTop = element.scrollHeight")
                time.sleep(2)  # Wait for new jobs to load
                new_height = await scrollable_list.evaluate("element => element.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            print("✅ All job listings are loaded.")
        except TimeoutError:
            print("❌ Could not find the job list. The page structure might have changed.")
            browser.close()
            return

        # Step 3: Get all job listing elements
        job_listings = page.locator('li.occludable-update').all()
        print(f"Found {len(job_listings)} job listings to scrape.")

        scraped_data = []

        # Step 4: Iterate through each job listing, click, and scrape details
        for i, listing in enumerate(job_listings):
            try:
                listing.click()
                # Wait for the right pane (job description) to update
                # A brief static wait is often sufficient here.
                time.sleep(1.5)

                # Scrape details from the right pane
                job_title_element = page.locator('h2.jobs-unified-top-card__job-title').first
                job_title = await job_title_element.inner_text() if await job_title_element.count() > 0 else "N/A"

                company_name_element = page.locator('span.jobs-unified-top-card__company-name').first
                company_name = await company_name_element.inner_text() if await company_name_element.count() > 0 else "N/A"

                # Based on your screenshot, this is the selector for the description
                description_element = page.locator('div.jobs-description-content__text').first
                description = await description_element.inner_text() if await description_element.count() > 0 else "N/A"

                print(f" Scraping Job #{i + 1}: {job_title} at {company_name}")

                scraped_data.append({
                    "Job Title": job_title,
                    "Company Name": company_name,
                    "Description": description.strip(),
                })

            except Exception as e:
                print(f"❌ Error scraping job #{i + 1}: {e}")

        browser.close()

        # Step 5: Store the data in a CSV file
        if scraped_data:
            df = pd.DataFrame(scraped_data)
            df.to_csv("linkedin_jobs.csv", index=False, encoding='utf-8')
            print("\n✅ Data successfully scraped and saved to linkedin_jobs.csv")
        else:
            print("\n⚠️ No data was scraped.")


if __name__ == "__main__":
    scrape_linkedin_jobs()