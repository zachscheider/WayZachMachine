import os
import sys
import csv
import re

from jinja2 import Environment, FileSystemLoader

import config
import archive

header = ['url', 'domain', 'base_url', 'title', 'file_name', 'page', 'archive_url']
env = Environment(loader=FileSystemLoader('templates'))

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

def parse_pocket_export(html_file, link_file):
  """Parse Pocket-format bookmarks export files (produced by getpocket.com/export/)"""

  html_file.seek(0)
  pattern = re.compile("^\\s*<li><a href=\"(.+)\" time_added=\"(\\d+)\" tags=\"(.*)\">(.+)</a></li>", re.UNICODE)
  for line in html_file:
    # example line
    # <li><a href="http://example.com/ time_added="1478739709" tags="tag1,tag2">example title</a></li>
    match = pattern.search(line)
    if match:
      fixed_url = match.group(1).replace('http://www.readability.com/read?url=', '')           # remove old readability prefixes to get original url
      writeLinkFile(link_file, fixed_url)

def writeLinkFile(link_file, fixed_url):
  w_or_a = 'w+'
  if os.path.isfile(link_file):
    w_or_a = 'a+'

  try:
    writer = open(link_file, w_or_a)
    writer.write(fixed_url + '\n')
    writer.close()
  except IOError as errno:
    print("I/O error: {0}".format(errno))    
  return

if __name__ == "__main__":
  argc = len(sys.argv)

  if argc < 2 or set(sys.argv).intersection(['-h', '--help']):
    print("Usage:")
    print("    python web_page.py --pocket ~/Downloads/ril_export.html ~/Downloads/bookmarks_export.txt\n")
    raise SystemExit(0)

  pocket_index = sys.argv.index("--pocket")+1
  pocket = sys.argv[pocket_index]
  with open(pocket, 'r', encoding='utf-8') as file:
    parse_pocket_export(file, sys.argv[pocket_index+1])