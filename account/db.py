# Import necessary packages here
# import re
import sqlite3
from typing import Any

import pandas as pd

# ==========================================================================================
# ==========================================================================================

# File:    db.py.py
# Date:    April 06, 2024
# Author:  Jonathan A. Webb
# Purpose: This file will read data from a SQLIte format
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class SQLiteDB:

    def __init__(self, database: str):
        self._database = database
        self._create_connection()

    # ------------------------------------------------------------------------------------------

    def __enter__(self):
        self._create_connection()
        return self

    # ------------------------------------------------------------------------------------------

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    # ------------------------------------------------------------------------------------------

    @property
    def conn(self) -> Any:
        """
        Protection for the _conn attribute
        """
        return self._conn

    # ------------------------------------------------------------------------------------------

    @property
    def cur(self) -> Any:
        """
        Protection for the _cur attribute
        """
        return self._cur

    # ------------------------------------------------------------------------------------------

    @property
    def database(self) -> Any:
        """
        Protection for the _database attribute
        """
        return self._database

    # ------------------------------------------------------------------------------------------

    def close_connection(self) -> None:
        """
        Close the connection to tjhe SQLite database
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------------------------------

    def get_database_tables(self, database: str = None) -> pd.DataFrame:
        rename = {"name": "Tables"}
        if database is None:
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
                df.rename(columns=rename, inplace=True)
            except sqlite3.Error as e:
                raise sqlite3.Error(f"Failed to retrieve tables: {e}")

            return df
        else:
            original_db = self.database
            self.close_connection()
            self._database = database
            self._create_connection()
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            try:
                df = pd.read_sql_query(query, self.conn)
                df.rename(columns=rename, inplace=True)
            except sqlite3.Error as e:
                raise sqlite3.Error(f"Failed to retrieve tables: {e}")
            self.close_connection()
            self._database = original_db
            self._create_connection()
            return df

    # ------------------------------------------------------------------------------------------

    def get_table_columns(self, table_name: str, database: str = None) -> pd.DataFrame:
        original_db = self.database
        if database is None:
            try:
                # Execute the PRAGMA command to get the table information
                self._cur.execute(f"PRAGMA table_info({table_name})")

                # Fetch all rows from the cursor
                rows = self._cur.fetchall()

                if len(rows) == 0:
                    raise sqlite3.Error(f"The table '{table_name}' does not exist.")

                # The names of the columns in the result set
                columns = ["id", "name", "type", "notnull", "default_value", "pk"]

                # Convert the result set to a DataFrame
                df = pd.DataFrame(rows, columns=columns)

                # Modify the DataFrame to match the output from the MySQLDB method
                df["Field"] = df["name"]
                df["Type"] = df["type"]
                df["Null"] = df["notnull"].map({0: "YES", 1: "NO"})
                df["Key"] = df["pk"].map({0: "", 1: "PRI"})
                df["Default"] = df["default_value"]
                df["Extra"] = ""

                # Only include the relevant columns in the DataFrame
                df = df[["Field", "Type", "Null", "Key", "Default", "Extra"]]

                return df

            except sqlite3.Error as e:
                # Handle any SQLite errors that occur
                raise sqlite3.Error(f"An error occurred: {e}")
        else:
            self.close_connection()
            self._database = database
            self._create_connection()
            try:
                # Execute the PRAGMA command to get the table information
                self._cur.execute(f"PRAGMA table_info({table_name})")

                # Fetch all rows from the cursor
                rows = self._cur.fetchall()

                if len(rows) == 0:
                    raise sqlite3.Error(f"The table '{table_name}' does not exist.")

                # The names of the columns in the result set
                columns = ["id", "name", "type", "notnull", "default_value", "pk"]

                # Convert the result set to a DataFrame
                df = pd.DataFrame(rows, columns=columns)

                # Modify the DataFrame to match the output from the MySQLDB method
                df["Field"] = df["name"]
                df["Type"] = df["type"]
                df["Null"] = df["notnull"].map({0: "YES", 1: "NO"})
                df["Key"] = df["pk"].map({0: "", 1: "PRI"})
                df["Default"] = df["default_value"]
                df["Extra"] = ""

                # Only include the relevant columns in the DataFrame
                df = df[["Field", "Type", "Null", "Key", "Default", "Extra"]]
                self._database = original_db
                self.close_connection()
                self._create_connection()

                return df

            except sqlite3.Error as e:
                self._database = original_db
                self.close_connection()
                self._create_connection()
                # Handle any SQLite errors that occur
                raise sqlite3.Error(f"An error occurred: {e}")

    # ------------------------------------------------------------------------------------------

    def execute_query(self, query: str, params: tuple = ()) -> pd.DataFrame:
        msg = "The number of placeholders in the query does not "
        msg += "match the number of parameters."
        query = query.replace("%s", "?")
        num_placeholders = query.count("?")
        if num_placeholders != len(params):
            raise ValueError(msg)
        try:
            if params:
                self._cur.execute(query, params)
            else:
                self._cur.execute(query)
            if (
                query.strip()
                .upper()
                .startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
            ):
                self._conn.commit()

            if self._cur.description:
                columns = [desc[0] for desc in self._cur.description]
                return pd.DataFrame(self._cur.fetchall(), columns=columns)
            else:
                self._conn.commit()
                return pd.DataFrame()

        except sqlite3.InterfaceError as e:
            # Handle errors related to the interface.
            raise sqlite3.Error(f"Failed to execute query: {e}")
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to execute query: {e}")

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_connection(self) -> None:
        """
        Create a connection to the SQLite database.
        """
        try:
            self._conn = sqlite3.connect(self.database)
            self._cur = self._conn.cursor()
        except sqlite3.DatabaseError as e:
            raise ConnectionError(
                f"Failed to create a connection due to DatabaseError: {e}"
            )


# ==========================================================================================
# ==========================================================================================


def create_position_table(position: str, database: str) -> None:
    query = f"""CREATE TABLE {position} (
        Date VARCHAR(10) NOT NULL,
        Credit REAL DEFAULT 0.0,
        Close REAL NOT NULL,
        PRIMARY KEY (Date)
    );
    """
    with SQLiteDB(database) as db:
        db.execute_query(query)


# -------------------------------------------------------------------------------------------


def create_fund_table(database: str) -> None:
    query = """CREATE TABLE Funds (
    Fund VARCHAR(8) NOT NULL,
    Status VARCHAR(8) CHECK (Status IN ('Active', 'Inactive')),
    PRIMARY KEY (Fund)
);
"""
    with SQLiteDB(database) as db:
        db.execute_query(query)


# ------------------------------------------------------------------------------------------


def create_database(database: str) -> None:
    create_fund_table(database)


# ------------------------------------------------------------------------------------------


def create_position_df(db_name: str, account: str) -> pd.DataFrame:
    query = f"SELECT * FROM {account};"
    with SQLiteDB(db_name) as db:
        df = db.execute_query(query)

    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%Y")

    # Create Cum Credit
    df["CumCredit"] = df["Credit"].cumsum()
    # Create daily delta value
    df["DollarDelta"] = df["Close"] - (df["Close"].shift(1) + df["Credit"])
    # Create %Delta per day
    df["PercDelta"] = df["DollarDelta"] / df["Close"] * 100.0
    # Create Cummulative % columm
    df["Percentage"] = ((df["Close"] / df["CumCredit"]) - 1.0) * 100.0

    df.sort_values(by="Date")
    return df


# ------------------------------------------------------------------------------------------


def create_funds_df(db_name: str) -> pd.DataFrame:
    query = "SELECT * FROM Funds;"
    with SQLiteDB(db_name) as db:
        return db.execute_query(query)


# ------------------------------------------------------------------------------------------


def get_database_tables(db_name: str) -> pd.DataFrame:
    with SQLiteDB(db_name) as db:
        return db.get_database_tables()


# ==========================================================================================
# ==========================================================================================
# eof
