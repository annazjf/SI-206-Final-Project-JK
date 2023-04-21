import sqlite3

def copy_database(src_file, dst_file):
    with sqlite3.connect(src_file) as src_conn, sqlite3.connect(dst_file) as dst_conn:
        # Get list of tables in source database
        tables = src_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        
        # Create each table in destination database
        for table_name in tables:
            table_name = table_name[0]
            src_schema = src_conn.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'").fetchone()[0]
            dst_conn.execute(src_schema)
        
        # Copy data from each table in source database
        for table_name in tables:
            table_name = table_name[0]
            src_table = src_conn.execute(f"SELECT * FROM {table_name}").fetchall()
            dst_conn.executemany(f"INSERT INTO {table_name} VALUES ({', '.join('?' * len(src_table[0]))})", src_table)
        dst_conn.commit()

if __name__ == '__main__':
    copy_database('founding_data.db', 'combined.db')
    copy_database('company_stock.db', 'combined.db')
