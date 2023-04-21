from bs4 import BeautifulSoup
import requests
import os
import csv
import sqlite3
import json
from datetime import datetime
import matplotlib.pyplot as plt

#Web scraping form Wikipedia website to get the tabel of S&P 500 companies information
def get_SP_companies_table():
  url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
  
  resp = requests.get(url)
  soup =  BeautifulSoup(resp.content, "html.parser")
  table = soup.find('table', id = "constituents")
  rows = []
  tbody = table.select('tbody')
  trs  = tbody[0].find_all('tr')
  #get the data in the following rows
  for tr in trs: # for every table row
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
  return rows

#Write the rows from scraping to a csv file
def write_row(rows, filename):
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for i, row in enumerate(rows):
            row_with_number = [i] + row # Add the number to the beginning of the row
            writer.writerow(row_with_number)

# set up database
def setUpDatabase (db_name):
   path = os.path.dirname(os.path.abspath('__file__'))
   conn = sqlite3.connect(path + "/" + db_name)
   cur = conn.cursor()
   return cur, conn

#create the sector dictionary and table where the id is the Sector_id in the companies table to make sure there is no duplicate string data
def creat_dict(cur2, conn2):
  dic = {}
  dic["Communication Services"] = 1
  dic["Consumer Discretionary"] = 2
  dic["Consumer Staples"] = 3
  dic["Energy"] = 4
  dic["Financials"] = 5
  dic["Health Care"] = 6
  dic["Industrials"] = 7
  dic["Information Technology"] = 8
  dic["Materials"] = 9
  dic["Real Estate"] = 10
  dic["Utilities"] = 11
  # cur2.execute("CREATE TABLE IF NOT EXISTS Sector (id INTEGER PRIMARY KEY, sector_name STRING UNIQUE)")
  # for i in dic:
  #   cur2.execute("INSERT INTO Sector (id, sector_name) VALUES(?,?)", (dic[i], i))
  # conn2.commit
  return dic

#Create the companies table and read the data from csv, insert it to the companies table 
def createdb (cur2, conn2, dicti ):
  # Check if the table exists
  cur2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
  table_exists = cur2.fetchone() is not None
  idx = 0
  if table_exists:
      # If the table exists, find the row number of the most recent id
      cur2.execute("SELECT MAX(id) FROM companies")
      idx = cur2.fetchone()[0]
  cur2.execute("CREATE TABLE IF NOT EXISTS companies (id PRIMARY KEY, Sector_id INTEGER, Date_added DATE)")
  # Read the CSV file and insert the remaining rows into the database
  with open('companies_data.csv', 'r',encoding='utf-8') as f:
      reader = csv.reader(f)
      next(reader)  # Skip the header row
      i = 0
      for row in reader:
          if not row[6]:
             continue
          if i >= idx:
              cur2.execute("INSERT OR IGNORE INTO companies (id, Sector_id, Date_added) VALUES (?,?,?)",(int(row[0]), dicti[row[3]],row[6]))
          if i == idx + 24:
              break
          i += 1

  # Commit changes and close the database connection
  conn2.commit()

#create a jason file with the dictionary where the keys are each of the sector name and the value is another dictionary stating the newest_added_date, oldest_added_date, andyears in S&P 500
def get_sector_dictionary(cur, conn):
  cur.execute("SELECT Sector_id, MAX(Date_added), MIN(Date_added), sector_name FROM companies JOIN Sector ON companies.Sector_id = Sector.id GROUP BY Sector_id")
  rows = cur.fetchall()
  # create a dictionary with GICS Sector as the key and the newest and oldest date added
  result_dict = {}
  for row in rows:
    dic = {}
    sectorname = row[3]
    newest_added_date = row[1]
    oldest_added_date = row[2]
    difference_years = round((datetime.strptime(newest_added_date, '%Y-%m-%d') - datetime.strptime(oldest_added_date, '%Y-%m-%d')).days / 365.25, 2)
    dic[sectorname] = {
        'newest_added_date': newest_added_date,
        'oldest_added_date': oldest_added_date,
        'difference_years': difference_years
    }
    result_dict.update(dic)
# write the result to a JSON file
  with open('result.json', 'w') as f:
    json.dump(result_dict, f, indent=4)
  conn.commit()
  return result_dict

#Plot the result to a bar graph stating the number of Years for Each Sector in S&P 500(sector name, years)
def plot_the_result (dic):
    Sector_name = dic.keys()
    years = []
    for i in dic:
      year = dic[i]["difference_years"]
      years.append(year)
    fig, ax = plt.subplots(figsize=(8, 7))
    plt.subplots_adjust(bottom=0.4)
    plt.bar(Sector_name, years)
    plt.xlabel('Sector Name')
    plt.ylabel('Years in S&P 500')
    plt.xticks(rotation=90)
    plt.title('Number of Years for Each Sector in S&P 500')
    plt.show()


if __name__ == '__main__':
   cur2, conn2 = setUpDatabase ("founding_data.db")
   dicti = creat_dict(cur2, conn2)
   createdb (cur2, conn2, dicti)
   rows = get_SP_companies_table()
   write_row (rows, "companies_data.csv")
  #  get_db_connection()
   result = get_sector_dictionary(cur2, conn2)
   plot_the_result (result)
