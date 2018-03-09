import os
import sys
import pytz
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
from subprocess import run, PIPE, DEVNULL
from time import strftime

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

def grab_link(link_file):
  # Read first line of file
  link = ""
  with open(link_file, 'r') as f:
    link = f.readline().strip()

  currTime = datetime.now(pytz.timezone(config.TIMEZONE)).strftime("%Y-%m-%d %H:%M:%S")
  theTitle = base_url(link) if link == "" else BeautifulSoup(urlopen(link), "lxml").title.string
  info = {
    'url': link,
    'domain': domain(link),
    'base_url': base_url(link),
    'title': theTitle,
    'file_name': file_name(link),
    'page': without_extension(file_name(link)),
    'archive_url': "",
    'timestamp': currTime
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

def archive_dot_org(link, timeout=config.TIMEOUT):
  """submit site to archive.org for archiving via their service, save returned archive url"""

  submit_url = 'https://web.archive.org/save/{}'.format(without_query(link['url']))

  success = False
  CMD = ['curl', '-I', submit_url]
  try:
    result = run(CMD, stdout=PIPE, stderr=DEVNULL, cwd=config.ARCHIVE_DIR, timeout=timeout + 1)  # archive.org.txt

    # Parse archive.org response headers
    headers = result.stdout.splitlines()
    content_location = [h for h in headers if b'Content-Location: ' in h]
    errors = [h for h in headers if h and b'X-Archive-Wayback-Runtime-Error: ' in h]

    if content_location:
      archive_path = content_location[0].split(b'Content-Location: ', 1)[-1].decode('utf-8')
      saved_url = 'https://web.archive.org{}'.format(archive_path)
      link['archive_url'] = saved_url
      success = True

    elif len(errors) == 1 and b'RobotAccessControlException' in errors[0]:
      output = submit_url
      raise Exception('Archive.org denied by {}/robots.txt'.format(link['domain']))
    elif errors:
      raise Exception(', '.join(e.decode() for e in errors))
    else:
      raise Exception('Failed to find "Content-Location" URL header in Archive.org response.')
  except Exception as e:
    print('       Visit url to see output:', ' '.join(CMD))

def fetch_favicon(link, timeout=config.TIMEOUT):
    """download site favicon from google's favicon api"""

    favPath = os.path.join(config.ARCHIVE_DIR, link['domain'])
    if os.path.exists(os.path.join(favPath, 'favicon.ico')):
        return

    CMD = ['curl', 'https://www.google.com/s2/favicons?domain={domain}'.format(**link)]
    fout = open('{}/favicon.ico'.format(favPath), 'w')
    try:
        run(CMD, stdout=fout, stderr=DEVNULL, cwd=favPath, timeout=timeout + 1)  # favicon.ico
        fout.close()
    except Exception as e:
        fout.close()
        print('       Run to see full output:', ' '.join(CMD))

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
    if config.FETCH_WGET:       fetch_wget(link_info)
    if config.FETCH_FAVICON:    fetch_favicon(link_info)
    if config.FETCH_PDF:        fetch_pdf(link_info)
    if config.FETCH_SCREENSHOT: fetch_screenshot(link_info)
    if config.SUBMIT_ARCHIVE:   archive_dot_org(link_info)
    rem_link(link_info, link_file)
    link_info = grab_link(link_file)
  
  # Creates index page from links stored in CSV
  csv_file = os.path.join(config.ARCHIVE_DIR, "index.csv")
  if os.path.exists(csv_file):
    web_page.ReadCSVasDict(csv_file)
