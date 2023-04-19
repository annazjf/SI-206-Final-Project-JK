from bs4 import BeautifulSoup
import requests
import os
import csv
import sqlite3

def get_SP_companies_table():
  url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
  resp = requests.get(url)
  soup =  BeautifulSoup(resp.content, "html.parser")
  table = soup.find('table', class_ = "wikitable sortable jquery-tablesorter")
  #get the headers
  headrow = []  
  rows = []
  trs = table.find_all('tr')
  headers = trs[0].find_all('th')
  for header in headers:
    headrow.append(header.text)
  rows.append(headrow)
  trs = trs[1:]
  data_row= []
  #get the data in the following rows
  for tr in trs: 
      data = tr.find_all('td')
      data_row.append(data.text)
      rows.append(data_row)
  return rows

def write_row (rows, filename):
    with open(filename, "w", encoding="utf-8-sig", newline = "") as f:
        writer = csv.writer(f)
        for row in rows:
          writer.writerow(row)

if __name__ == '__main__':
   rows = get_SP_companies_table()
   write_row (rows, companies_data.csv)