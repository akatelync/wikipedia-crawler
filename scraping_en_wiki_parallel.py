import time
import pandas as pd
import concurrent.futures

from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def find_philosophy(
    start_url: str = "https://en.wikipedia.org/wiki/Special:Random",
    target_url: str = "https://en.wikipedia.org/wiki/Philosophy",
) -> Tuple[str, str, int, int]:

    next_url = start_url
    last_url = next_url
    visited_urls = set()
    degrees = 0
    href_count = 0
    all_followed_links = []

    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        path = "/usr/local/bin/chromedriver"
        chrome_service = webdriver.ChromeService(executable_path=path)
        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.get(start_url)
        starting_title = driver.title

        while True:
            if next_url in visited_urls:
                degrees = -1
                last_url = next_url
                break

            if next_url == target_url:
                break

            visited_urls.add(next_url)
            driver.get(next_url)

            try:
                main_content = driver.find_element("id", "mw-content-text")
                links = main_content.find_elements(
                    By.CSS_SELECTOR, "div.mw-parser-output > p a")

                found_valid_link = False

                followed_links = []
                for link in links[:5]:
                    href = link.get_attribute("href")
                    if (
                        href and "/wiki" in href and
                        ":" not in href.split("/wiki/")[-1] and
                        "cite_note" not in href
                    ):
                        next_url = href
                        followed_links.append(next_url)
                        found_valid_link = True
                        degrees += 1
                        href_count += 1
                        break

                all_followed_links.append(followed_links)

                if not found_valid_link:
                    degrees = -2
                    break

            except NoSuchElementException:
                degrees = -3
                break

            time.sleep(0.5)

    finally:
        driver.quit()

    return (starting_title, all_followed_links, degrees, href_count)


def process_batch(
    urls: List[str],
    current_count: int,
    total_pages: int,
) -> List[Tuple[str, str, int, int]]:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_url = {executor.submit(
            find_philosophy, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            results.append(future.result())
            current_count += 1
            print(
                f"\r{current_count}/{total_pages} pages processed ({(current_count/total_pages)*100:.1f}%)", end="")
    return results


def main():
    num_pages = 1000
    batch_size = 30
    all_results = []
    processed_count = 0

    print("Starting the road to Philosophy...")
    start_time = time.time()

    for i in range(0, num_pages, batch_size):
        batch_urls = [
            "https://en.wikipedia.org/wiki/Special:Random" for _ in range(min(batch_size, num_pages - i))]
        batch_results = process_batch(batch_urls, processed_count, num_pages)
        all_results.extend(batch_results)
        processed_count += len(batch_results)
        time.sleep(0.5)

    print("\n")

    df = pd.DataFrame(all_results, columns=[
                      "starting_url", "link_tree", "degrees", "href_count"])

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f'en_philosophy_results_{timestamp}.csv'
    df.to_csv(filename, index=False)

    execution_time = time.time() - start_time

    print("\nDONE!!!!")
    print("-" * 50)
    print(f"Total execution time: {execution_time:.1f} seconds")
    print(f"Results saved to: {filename}")


if __name__ == "__main__":
    main()
