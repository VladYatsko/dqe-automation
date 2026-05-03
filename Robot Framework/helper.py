import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from IPython.display import display

from pandas import to_datetime

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


def read_html_table_to_dataframe(html_file_path: str, filter_date) -> pd.DataFrame:
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
            table_result.sort_values(by='Facility Type', ascending=True, inplace=True)

            table_result['Average Time Spent'] = pd.to_numeric(table_result['Average Time Spent'], errors='coerce')
            # 2. Fill any NaNs that might have been created during conversion
            table_result['Average Time Spent'] = table_result['Average Time Spent'].fillna(0)  # or another default
            # 3. Convert the column to the required integer type (int64)
            table_result['Average Time Spent'] = table_result['Average Time Spent'].astype('int64')

            filtered_df = table_result[table_result['Visit Date'] == filter_date]
            # table_result.to_csv("output_table/table.csv", index=False)

            columns_to_select = ['Facility Type', 'Visit Date', 'Average Time Spent']
            selected_columns_df = filtered_df[columns_to_select]

            return selected_columns_df
            print("Dataset created")

            # print(f"Table content has been successfully saved to {csv_file_path}")

        except TimeoutException:
            print("Error: No table element was found on the page within 10 seconds.")
        except NoSuchElementException:
            print("Error: Could not find header or row elements within the table. Check the table structure.")
        except FileNotFoundError:
            print(f"Error: The file '{html_file_path}' was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def read_parquet_to_dataframe(folder_path: str, filter_date) -> pd.DataFrame:
    """
    Reads a partitioned Parquet dataset into a Pandas DataFrame.
    It can optionally filter the data by a date partition.

    Note: This function assumes the dataset is partitioned by a column named 'date'
    with string values in 'YYYY-MM-DD' format.
    """
    filters = [('visit_date', '==', to_datetime(filter_date).normalize())] if filter_date else None
    try:
        df = pd.read_parquet(folder_path, filters=filters)
        # After filtering, the partition column ('date') might be categorical.
        # Convert it to string to ensure consistency for comparison.
        if 'visit_date' in df.columns:
            df['visit_date'] = df['visit_date'].astype(str)
        df['avg_time_spent'] = pd.to_numeric(df['avg_time_spent'], errors='coerce')
        df['avg_time_spent'] = df['avg_time_spent'].fillna(0)

        # Round AND convert to integer type
        df['avg_time_spent'] = df['avg_time_spent'].round(0).astype(int)
        df.sort_values(by='facility_type', ascending=True, inplace=True)
        df['avg_time_spent'] = pd.to_numeric(df['avg_time_spent'], errors='coerce')

        # Fill any NaNs that might have been created during conversion
        df['avg_time_spent'] = df['avg_time_spent'].fillna(0)  # or another default

        # Convert the column to the required integer type (int64)
        df['avg_time_spent'] = df['avg_time_spent'].astype('int64')

        columns_to_select = ['facility_type', 'visit_date', 'avg_time_spent']

        # Select the specific columns you need from the filtered result
        selected_columns_df = df[columns_to_select]
        selected_columns_df = selected_columns_df.rename(columns={'avg_time_spent': 'average_time_spent'})

        return selected_columns_df.reset_index(drop=True)

    except Exception as e:
        raise RuntimeError(f"Failed to read Parquet dataset from {folder_path}: {e}")

def compare_dataframes(df1, df2):
    # Standardize column names (optional, depends on your use case)
    # Convert all column names to lowercase and strip spaces for robust comparison
    df1.columns = df1.columns.str.lower().str.replace(' ', '_')
    df2.columns = df2.columns.str.lower().str.replace(' ', '_')

    # Sort both DataFrames by a shared column to ignore row order (e.g., 'facility_type')
    df1_normalized = df1.sort_values(by='facility_type').reset_index(drop=True)
    df2_normalized = df2.sort_values(by='facility_type').reset_index(drop=True)

    # Use pandas testing function for a detailed comparison that ignores index differences
    try:
        pd.testing.assert_frame_equal(df1_normalized, df2_normalized)
        # Explicitly tells the comparison to ignore the index values
        return True, "DataFrames match."
    except AssertionError as e:
        return False, f"DataFrames do not match:\n{e}"
