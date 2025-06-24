import sqlite3

conn = sqlite3.connect('imdb.db')

print('Tables:')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f"  {table[0]}")

print('\nTable counts:')
for table in tables:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"  {table[0]}: {count}")
    except Exception as e:
        print(f"  {table[0]}: Error - {e}")

print('\nSample data from title_basics:')
try:
    sample = conn.execute("SELECT primaryTitle, startYear, genres FROM title_basics WHERE primaryTitle IS NOT NULL LIMIT 10").fetchall()
    for row in sample:
        print(f"  {row}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
