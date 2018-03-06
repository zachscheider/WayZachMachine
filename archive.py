import os
import sys
from subprocess import run, PIPE, DEVNULL

import config
import web_page

# URL helpers
without_scheme = lambda url: url.replace('http://', '').replace('https://', '').replace('ftp://', '')
without_query = lambda url: url.split('?', 1)[0]
without_hash = lambda url: url.split('#', 1)[0]
without_path = lambda url: url.split('/', 1)[0]
file_name = lambda url: url.split('/')[-1]
without_extension = lambda file_name: file_name.split('.')[0]
domain = lambda url: without_hash(without_query(without_path(without_scheme(url))))
base_url = lambda url: without_query(without_scheme(url))[:without_query(without_scheme(url)).rfind('/')+1]

def grab_link(path):
  # Read first line of file
  link = ""
  with open(link_file, 'r') as f:
    link = f.readline().strip()

  info = {
    'url': link,
    'domain': domain(link),
    'base_url': base_url(link),
    'title': base_url(link),
    'file_name': file_name(link),
    'page': without_extension(file_name(link))
  }
  return info

def fetch_wget(link, timeout=config.TIMEOUT):
  CMD = [
    *'wget -E -H -k -p -e robots=off'.split(' '),
    link['url'],
  ]

  try:
    result = run(CMD, stdout=PIPE, stderr=PIPE, cwd=config.ARCHIVE_DIR, timeout=timeout + 1)  # index.html
    if result.returncode > 0:
      print('       got wget response code {}:'.format(result.returncode))
      print('\n'.join('         ' + line for line in (result.stderr or result.stdout).decode().rsplit('\n', 10)[-10:] if line.strip()))
      raise Exception('Failed to wget download')
  except Exception as e:
    print('       Run to see full output:', 'cd {}; {}'.format(config.ARCHIVE_DIR, ' '.join(CMD)))

def fetch_pdf(link, timeout=config.TIMEOUT):
  CMD = [
    *'chromium-browser --headless --disable-gpu'.split(' '),
    '--print-to-pdf='+link['page']+'.pdf',
    link['url'],
  ]
  pdf_file = os.path.join(config.ARCHIVE_DIR, link['base_url'])
  try:
    result = run(CMD, stdout=PIPE, stderr=PIPE, cwd=pdf_file, timeout=timeout + 1)  # output.pdf
    if result.returncode:
      print('     ', (result.stderr or result.stdout).decode())
      raise Exception('Failed to print PDF')
  except Exception as e:
    print('       Run to see full output:', 'cd {}; {}'.format(pdf_file, ' '.join(CMD)))

def fetch_screenshot(link, timeout=config.TIMEOUT):
  CMD = [
    *'chromium-browser --headless --disable-gpu'.split(' '),
    '--screenshot='+link['page']+'.png',
    link['url'],
  ]
  pdf_file = os.path.join(config.ARCHIVE_DIR, link['base_url'])
  try:
    result = run(CMD, stdout=PIPE, stderr=PIPE, cwd=pdf_file, timeout=timeout + 1)  # output.pdf
    if result.returncode:
      print('     ', (result.stderr or result.stdout).decode())
      raise Exception('Failed to print PDF')
  except Exception as e:
    print('       Run to see full output:', 'cd {}; {}'.format(pdf_file, ' '.join(CMD)))

def rem_link(link, link_file, timeout=config.TIMEOUT):
  CMD = [
    *'sed -i 1d'.split(' '),
    link_file,
  ]

  csv_file = os.path.join(config.ARCHIVE_DIR, "index.csv")
  web_page.WriteDictToCSV(csv_file, link)

  try:
    result = run(CMD, stdout=PIPE, stderr=PIPE, cwd=config.ROOT_FOLDER, timeout=timeout + 1)
    if result.returncode > 0:
      print('     ', (result.stderr or result.stdout).decode())
      raise Exception('Failed to remove link from queue')
  except Exception as e:
    print('       Run to see full output:', 'cd {}; {}'.format(config.ROOT_FOLDER, ' '.join(CMD)))

if __name__ == "__main__":
  argc = len(sys.argv)

  if argc < 2 or set(sys.argv).intersection(['-h', '--help']):
    print("Usage:")
    print("    python archive.py ~/Downloads/bookmarks_export.txt\n")
    raise SystemExit(0)

  link_file = sys.argv[1]

  if not os.path.exists(config.ARCHIVE_DIR):
    os.makedirs(config.ARCHIVE_DIR)

  # Loops through entire file, removing successfully downloaded links
  link_info = grab_link(link_file)
  while link_info['url'].strip():
    fetch_wget(link_info)
    fetch_pdf(link_info)
    fetch_screenshot(link_info)
    rem_link(link_info, link_file)
    link_info = grab_link(link_file)
  
  # Creates index page from links stored in CSV
  csv_file = os.path.join(config.ARCHIVE_DIR, "index.csv")
  web_page.ReadCSVasDict(csv_file)