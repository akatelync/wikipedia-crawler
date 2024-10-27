# Wikipedia Crawler

Directory:

`LT6-Lab-APIs.ipynb`
- notebook demonstrating results of scraping a single Wikipedia page
- analyzes degrees of separation and distribution among multiple Wikipedia pages

`scraping_en_parallel.py`
- implementation of parallel processing of English Wikipedia for loop for 1000 pages
- saves results of scraping `(starting page, degrees)` to `results_20241027-063423.csv`
- *CAUTION: works on MacOS M1, untested on PC*

`scraping_ceb_parallel.py`
- implementation of parallel processing of Cebuano Wikipedia for loop for 1000 pages
- saves results of scraping `(starting page, termination page, termination reason, degrees)` to `results_20241027-083929.csv`
- *CAUTION: works on MacOS M1, untested on PC*