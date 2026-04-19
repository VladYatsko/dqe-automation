import pandas as pd


class DataQualityLibrary:
    @staticmethod
    def check_duplicates(df, column_names=None):
        if column_names:
            duplicates = df.duplicated(subset=column_names)
        else:
            duplicates = df.duplicated()
        assert not duplicates.any(), f"Found duplicate rows in columns: {column_names if column_names else 'all columns'}"

    @staticmethod
    def check_count(df1, df2):
        assert len(df1) == len(df2), f"Row count mismatch: {len(df1)} != {len(df2)}"

    @staticmethod
    def check_data_full_data_set(df1, df2):
        pd.testing.assert_frame_equal(df1.reset_index(drop=True), df2.reset_index(drop=True))

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert not df.empty, "DataFrame is empty"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        if column_names is None:
            column_names = df.columns
        for col in column_names:
            assert df[col].notnull().all(), f"Null values found in column: {col}"

# import pandas as pd
#
#
# class DataQualityLibrary:
#     """
#     A library of static methods for performing data quality checks on pandas DataFrames.
#
#     This class is intended to be used in a PyTest-based testing framework to validate
#     the quality of data in DataFrames. Each method performs a specific data quality
#     check and uses assertions to ensure that the data meets the expected conditions.
#     """
#
#     @staticmethod
#     def check_duplicates(df, column_names=None):
#         if column_names:
#             df.duplicates(column_names)
#         else:
#             df.duplicates(all_columns)
#
#     @staticmethod
#     def check_count(df1, df2):
#         df1.count = df2.count
#
#     @staticmethod
#     def check_data_full_data_set(df1, df2):
#         df1 = df2
#
#     @staticmethod
#     def check_dataset_is_not_empty(df):
#         df.is_not_empty
#
#     @staticmethod
#     def check_not_null_values(df, column_names=None):
#         col for df.column_names:
#             col.not_null