import csv
import os
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

output_dir = os.path.join(os.getcwd(), "output_table")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created folder: {output_dir}")
else:
    print(f"Folder already exists: {output_dir}")

class WebDriverManager:
    """A context manager for initializing and quitting the Selenium WebDriver."""

    def __init__(self, driver_type='Chrome'):
        self.driver = None
        self.driver_type = driver_type

    def __enter__(self):
        """Initializes the WebDriver."""
        try:
            if self.driver_type == 'Chrome':
                self.driver = webdriver.Chrome()
            else:
                raise ValueError("Unsupported driver type")

            return self.driver
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Quits the WebDriver to ensure proper cleanup."""
        if self.driver:
            self.driver.quit()
        return False


def extract_table_to_csv(html_file_path, csv_file_path):
    """
    Extracts a table from a local HTML file and saves its content to a CSV file.
    """
    with WebDriverManager(driver_type='Chrome') as driver:
        try:
            full_html_path = 'file://' + os.path.abspath(html_file_path)
            driver.get(full_html_path)

            # 1. Wait for the table to be present using its table name.
            wait = WebDriverWait(driver, 10)
            table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
            print("Table found successfully using its tag name.")

            # 2. Read all data rows.
            data = {}
            columns = table.find_elements(By.CLASS_NAME, "y-column")

            for col_index, column in enumerate(columns):
                header_block = column.find_element( By.ID, "header")
                header_text = header_block.text.strip() if header_block else f"Column_{col_index + 1}"

                column_cells = []
                column_blocks = column.find_elements(By.CSS_SELECTOR, "g.column-block")
                for block in column_blocks:
                    if block.get_attribute("id") == "header":
                        continue
                    cells_container = block.find_element( By.CLASS_NAME, "column-cells")
                    if cells_container:
                        cells = cells_container.find_elements(By.CLASS_NAME, "column-cell")
                        for cell in cells:
                            column_cells.append(cell.text.strip())

                data[header_text] = column_cells

            # 3. Write the extracted headers and data to a CSV file.
            table_result = pd.DataFrame({k: pd.Series(v) for k, v in data.items()})
            table_result.to_csv("output_table/table.csv", index=False)
            print("Table saved to table.csv")

            print(f"Table content has been successfully saved to {csv_file_path}")

        except TimeoutException:
            print("Error: No table element was found on the page within 10 seconds.")
        except NoSuchElementException:
            print("Error: Could not find header or row elements within the table. Check the table structure.")
        except FileNotFoundError:
            print(f"Error: The file '{html_file_path}' was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    html_report_file = "../Selenium Introduction/source_report.html"
    csv_output_file = "output_table/table.csv"

    extract_table_to_csv(html_report_file, csv_output_file)
