import os
import csv

from datetime import datetime
from string import Template

import config

header = ['url', 'domain', 'base_url', 'title', 'file_name', 'page']

def ReadCSVasDict(csv_file):
  try:
    with open(csv_file) as csvfile:
      reader = csv.DictReader(csvfile)
      return reader
  except IOError as errno:
    print("I/O error: {0}".format(errno))    
  return

def WriteDictToCSV(csv_file, dict_data, csv_columns=header):
  w_or_a = 'w'
  if os.path.isfile(csv_file):
    w_or_a = 'a'

  try:
    with open(csv_file, w_or_a, newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
      if w_or_a == 'w':
        writer.writeheader()
      writer.writerow(dict_data)
  except IOError as errno:
    print("I/O error: {0}".format(errno))    
  return