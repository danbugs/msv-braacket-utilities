import datetime
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Selenium to suppress debugging output
chrome_options = Options()
chrome_options.add_argument("--log-level=3")
service = ChromeService()

# Generate file names based on current datetime
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"most-improved-{current_time}.txt"
sorted_output_filename = f"most-improved-{current_time}-sorted.txt"

default_url = "https://braacket.com/league/MSVS/ranking/61481DD2-6EF1-40F8-82A7-6EF1769AE8DE?rows=200"

# Check if an argument is provided
if len(sys.argv) > 1:
    first_arg = sys.argv[1]
    
    if first_arg.startswith("http://") or first_arg.startswith("https://"):
        # Argument is a URL
        url = first_arg
        input_filename = None
    else:
        # Argument is assumed to be a file
        input_filename = first_arg
        url = None 
else:
    # No argument provided, use default URL
    url = default_url
    input_filename = None

if input_filename:
    # Sorting mode
    with open(input_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    sorted_lines = sorted(lines, key=lambda x: int(x.split("DELTA: ")[-1]), reverse=True)

    sorted_output_filename = f"most-improved-{current_time}-sorted.txt"
    with open(sorted_output_filename, "w", encoding="utf-8") as sorted_file:
        sorted_file.writelines(sorted_lines)

    print(f"Sorted output written to {sorted_output_filename}")

else:
    # Scraping mode
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open file for writing player data
    with open(output_filename, "w", encoding="utf-8") as file:
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "table-hover")))

            players = driver.find_elements(By.CSS_SELECTOR, "tr a.ellipsis, tr.text-bold a, tr a")
            total_players = len(players)
            print(f"Total players found: {total_players}")

            # Start from the 8th player and skip the last player
            for i in range(7, total_players - 1):
                try:
                    players = driver.find_elements(By.CSS_SELECTOR, "tr a.ellipsis, tr.text-bold a, tr a")
                    player = players[i]
                    player_name = player.text
                    player.click()

                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "display_ranking")))
                    data_table_input = driver.find_element(By.ID, "display_ranking")
                    driver.execute_script("arguments[0].click();", data_table_input)

                    time.sleep(5)

                    table_data = None
                    attempts = 0
                    while attempts < 3 and not table_data:
                        table_data = driver.execute_script("""
                            let rows = document.querySelectorAll("div[aria-label='A tabular representation of the data in the chart.'] table tbody tr");
                            let data = [];
                            rows.forEach(row => {
                                let cells = row.querySelectorAll("td");
                                let rowData = [];
                                cells.forEach(cell => {
                                    rowData.push(cell.innerText);
                                });
                                data.push(rowData);
                            });
                            return data;
                        """)
                        if not table_data:
                            time.sleep(5)
                        attempts += 1

                    if table_data:
                        first_row = table_data[0]
                        last_row = table_data[-1]
                        start_value = int(first_row[1].replace(",", ""))
                        end_value = int(last_row[1].replace(",", ""))
                        delta_value = end_value - start_value
                        output_line = f"{player_name}: START: {start_value}, END: {end_value}, DELTA: {delta_value}"
                        print(output_line)
                        file.write(output_line + "\n")

                    driver.back()
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "table-hover")))

                except Exception as e:
                    print(f"Error processing player {i + 1}: {e}")
                    driver.get("https://braacket.com/league/MSVS/ranking/61481DD2-6EF1-40F8-82A7-6EF1769AE8DE?rows=200")
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "table-hover")))
                    continue

        finally:
            driver.quit()

    print(f"Output written to {output_filename}")
