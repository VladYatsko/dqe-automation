import pandas as pd


class ParquetReader:
    @staticmethod
    def read_parquet(file_path, columns=None):
        if columns:
            return pd.read_parquet(file_path, columns=columns)
        return pd.read_parquet(file_path)
