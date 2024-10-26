import time
import pandas as pd
import multiprocessing as mp

from typing import Tuple
from selenium import webdriver
from multiprocessing import Pool, cpu_count
from selenium.webdriver.common.by import By
from concurrent.futures import ProcessPoolExecutor
from selenium.common.exceptions import NoSuchElementException

def find_philosophy(
        start_url: str = "https://en.wikipedia.org/wiki/Special:Random",
        target_url: str = "https://en.wikipedia.org/wiki/Philosophy",
) -> Tuple[str, int]:
    
	next_url = start_url
	visited_urls = set()
	degrees = 0

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
				print("Loop detected!")
				break

			if next_url == target_url:
				print("Philosophy has been reached!")
				break

			visited_urls.add(next_url)
			driver.get(next_url)

			try:
				main_content = driver.find_element("id", "mw-content-text")
				links = main_content.find_elements(By.CSS_SELECTOR, "div.mw-parser-output > p a")

				found_valid_link = False

				for link in links[:5]:
					href = link.get_attribute("href")
					if (
						href and "/wiki" in href and
						":" not in href.split("/wiki/")[-1] and
						"cite_note" not in href
					):
						next_url = href
						found_valid_link = True
						degrees +=1
						break

				if not found_valid_link:
					degrees = -1
					print("Invalid link!")
					break

			except NoSuchElementException:
				degrees = -1
				break

			time.sleep(0.5)

	finally:
		driver.quit()

	return (starting_title, degrees)

def process_single():
    """Process a single item"""
    return find_philosophy()

def parallel_process(n_items=1000):
    """
    Process items in parallel with simple progress tracking and save results to CSV
    """
    n_processes = min(6, mp.cpu_count())
    results = {}
    
    print(f"Starting processing with {n_processes} processes...")
    start_time = time.time()
    items_processed = 0
    
    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        futures = [executor.submit(process_single) for _ in range(n_items)]
        
        for future in futures:
            try:
                key, value = future.result()
                results[key] = value
                items_processed += 1
                
                if items_processed % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = items_processed / elapsed if elapsed > 0 else 0
                    print(f"\rProcessed {items_processed}/{n_items} items "
                          f"({(items_processed/n_items*100):.1f}%) "
                          f"[{rate:.1f} items/s]\n", end="", flush=True)
                    
            except Exception as e:
                print(f"\nError processing item: {str(e)}")
                continue
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n\nCompleted! Processed {len(results)} items in {total_time:.2f} seconds "
          f"({len(results)/total_time:.1f} items/s)")
    
    df = pd.DataFrame(list(results.items()), columns=['first_page', 'degrees'])
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    csv_filename = f"results_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\nResults saved to {csv_filename}")
    
    return df, results

if __name__ == '__main__':
    results = parallel_process()