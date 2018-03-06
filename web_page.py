import os
import csv

from datetime import datetime
from string import Template
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

import config

header = ['url', 'domain', 'base_url', 'title', 'file_name', 'page']
env = Environment(loader=FileSystemLoader('templates'))
#env = Environment(
  #loader=PackageLoader('web_page', 'templates'),
  #autoescape=select_autoescape(['html', 'xml'])
#)

def ReadCSVasDict(csv_file):
  link_dict = []
  try:
    with open(csv_file) as csvfile:
      reader = csv.DictReader(csvfile)
      for line in reader:
        link_dict.append(line)
      template = env.get_template('index.html')
      render_index = str.encode(template.render(items=link_dict))
      with open(os.path.join(config.ARCHIVE_DIR, "index.html"), "wb") as fh:
        fh.write(render_index)
      return link_dict
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