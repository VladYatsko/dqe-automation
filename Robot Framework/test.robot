
*** Settings ***
Documentation     A test suite to compare data from an HTML report and a Parquet dataset.
Library           SeleniumLibrary
Library           helper.py          # Imports functions as keywords
Test Teardown     Close Browser      # Ensures browser closes after every test case

*** Variables ***
# --- Paths should be absolute or relative to the execution directory ---
${REPORT_FILE}      ${CURDIR}/source_report.html
${PARQUET_FOLDER}   ${CURDIR}/parquet_data/facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}      2025-10-29
${BROWSER}          Chrome
# --- Adjust the locator to match the ID or XPath of your specific table ---
${TABLE_LOCATOR}    class=y-column

*** Test Cases ***
Compare HTML Table Data With Parquet Data
    [Documentation]    This test opens an HTML report, reads a data table,
    ...    and compares it against a filtered Parquet dataset.

    # Step 1: Read table data into a DataFrame using the helper function.
    # We call helper.py's functions directly using their Python names (case-insensitive in Robot)
    ${html_df}=    Read Html Table To Dataframe    ${REPORT_FILE}    ${FILTER_DATE}
    Log To Console    \n--- Filtered HTML DataFrame ---\n${html_df}

    # Step 2: Read Parquet data with filtering using the helper function.
    ${parquet_df}=    Read Parquet To Dataframe    ${PARQUET_FOLDER}    ${FILTER_DATE}
    Log To Console    \n--- Filtered Parquet DataFrame ---\n${parquet_df}

    # Step 3: Compare both DataFrames using the helper function, wrap in a check.
    Compare Dataframes And Fail On Mismatch    ${html_df}    ${parquet_df}


*** Keywords ***
# These keywords wrap the helper functions to handle the final Fail condition
Compare Dataframes And Fail On Mismatch
    [Arguments]    ${df1}    ${df2}
    [Documentation]    Compares two DataFrames and fails the test with a detailed message if they are not equal.

    # Calls the Python function compare_dataframes from helper.py
    ${are_equal}    ${message}=    Compare Dataframes    ${df1}    ${df2}

    IF    not ${are_equal}
        Fail    DataFrames do not match. Details:\n${message}
    ELSE
        Log    Comparison successful: ${message}
    END