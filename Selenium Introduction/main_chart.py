import os
import time
import pandas as pd
from selenium.webdriver.common.by import By

output_dir = os.path.join(os.getcwd(), "output_chart")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created folder: {output_dir}")
else:
    print(f"Folder already exists: {output_dir}")

def safe_find_element(driver, by, value, timeout=10):
    """Safely find an element, return None if not found."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except Exception:
        return None

def safe_screenshot(driver, element, path):
    """Take a screenshot safely"""
    try:
        size = element.size
        if size['width'] > 0 and size['height'] > 0:
            element.screenshot(path)
        else:
            print(f"Element has zero size, taking full page screenshot: {path}")
            driver.save_screenshot(path)
    except Exception as e:
        print(f"Failed to take screenshot {path}: {e}")

def extract_chart_data(chart_element):
    """Extract data from doughnut chart."""
    data = []
    slices = chart_element.find_elements(By.CSS_SELECTOR, "g.slice")
    for slice_ in slices:
        tspan_elements = slice_.find_elements(By.CSS_SELECTOR, "g.slicetext text tspan")
        if len(tspan_elements) >= 2:
            data.append({
                "Facility Type": tspan_elements[0].text.strip(),
                "Min Average Time Spent": tspan_elements[1].text.strip()
            })
    return pd.DataFrame(data)

def interact_doughnut_chart_with_legend(driver, chart_selector='svg', legend_selector='legend', legend_item_class='traces', screenshot_dir='output_chart'):
    screenshot_counter = 0
    chart = safe_find_element(driver, By.CSS_SELECTOR, chart_selector)
    if not chart:
        print("Chart not found.")
        return

    # Initial screenshot and data
    safe_screenshot(driver, chart, f"{screenshot_dir}/output_chart{screenshot_counter}.png")
    extract_chart_data(chart).to_csv(f"{screenshot_dir}/output_chart{screenshot_counter}.csv", index=False)
    screenshot_counter += 1

    # Find legend and legend items
    legend = safe_find_element(driver, By.CLASS_NAME, legend_selector)
    if not legend:
        print("Legend not found.")
        return

    legend_items = legend.find_elements(By.CLASS_NAME, legend_item_class)
    print(f"Found {len(legend_items)} legend items")

    for legend_item in legend_items:
        try:
            legend_item.click()
            time.sleep(1)  # Wait for chart to update
            chart = safe_find_element(driver, By.CSS_SELECTOR, chart_selector)
            safe_screenshot(driver, chart, f"{screenshot_dir}/output_chart{screenshot_counter}.png")
            extract_chart_data(chart).to_csv(f"{screenshot_dir}/output_chart{screenshot_counter}.csv", index=False)
            screenshot_counter += 1
        except Exception as e:
            print(f"Failed to apply legend filter or capture chart: {e}")

# Example usage:

from selenium import webdriver
driver = webdriver.Chrome()
full_html_path = 'file://' + os.path.abspath("../Selenium Introduction/source_report.html")
driver.get(full_html_path)
interact_doughnut_chart_with_legend(driver)
