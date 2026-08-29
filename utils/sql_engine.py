import sqlite3
import pandas as pd


def create_connection(database_path):
    connection = sqlite3.connect(database_path)
    return connection


def run_query(connection, query):
    result = pd.read_sql_query(query, connection)
    return result