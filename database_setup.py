# ==============================================================================
# FILE: database_setup.py
#
# PURPOSE: Reads the stock market CSV, cleans the data, and loads it into a
#          SQLite database. This script should be run once to set up the DB.
# ==============================================================================
import pandas as pd
from sqlalchemy import create_engine, text
import re
import os

def clean_col_names(df):
    """Cleans DataFrame column names to be valid SQL/Python identifiers."""
    cols = df.columns
    new_cols = []
    for col in cols:
        # Lowercase, replace special chars with underscore, remove leading/trailing junk
        new_col = re.sub(r'[^0-9a-zA-Z_]+', '_', col).lower()
        new_col = new_col.strip('_')
        # Ensure it's a valid identifier (doesn't start with a number)
        if new_col and new_col[0].isdigit():
            new_col = '_' + new_col
        new_cols.append(new_col)
    df.columns = new_cols
    return df

def setup_database():
    """Main function to perform the database setup."""
    csv_file_path = 'Stock Market Dataset 2.csv'
    db_file_path = 'stock_market.db'
    table_name = 'stock_data'

    if not os.path.exists(csv_file_path):
        print(f"Error: The file '{csv_file_path}' was not found.")
        print("Please make sure the dataset is in the same directory as this script.")
        return

    # If database already exists, remove it to start fresh
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
        print(f"Removed existing database '{db_file_path}'.")

    print("Reading and cleaning stock market data...")
    # Read the CSV
    df = pd.read_csv(csv_file_path)

    # Clean column names
    df = clean_col_names(df)
    
    # Drop the original unnamed index column if it exists
    if 'unnamed_0' in df.columns:
        df = df.drop(columns=['unnamed_0'])

    # Convert date column
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Clean numeric columns by removing commas and converting to float
    for col in df.columns:
        # Only process object columns that are not the date column
        if df[col].dtype == 'object' and col != 'date':
            # Ensure the column is treated as a string before using .str accessor
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where date is NaT (Not a Time) after conversion
    df.dropna(subset=['date'], inplace=True)
    
    # The primary key in enrichmcp should not be null.
    # We add a simple integer primary key.
    df.insert(0, 'id', range(1, 1 + len(df)))

    print(f"Cleaned Data Head:\n{df.head()}")
    print(f"\nData Types:\n{df.dtypes}")

    # Create SQLite engine and load data
    engine = create_engine(f'sqlite:///{db_file_path}')
    print(f"\nLoading data into '{table_name}' table in '{db_file_path}'...")
    
    # Use pandas to_sql to create the table and insert the data
    df.to_sql(table_name, engine, if_exists='replace', index=False)

    # Verify the data insertion
    with engine.connect() as connection:
        result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar_one()
        print(f"Successfully loaded {count} rows into the database.")
        
    print("Database setup complete.")


if __name__ == "__main__":
    setup_database() 