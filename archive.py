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
base_url = lambda url: without_query(without_scheme(url))

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

def fetch_wget(link, link_file, timeout=config.TIMEOUT):
  CMD = [
    *'wget -E -H -k -p -e robots=off'.split(' '),
    link['url'],
  ]

  try:
    result = run(CMD, stdout=PIPE, stderr=PIPE, cwd=config.ARCHIVE_DIR, timeout=timeout + 1)  # index.html
    if result.returncode > 0:
      print('       got wget response code {}:'.format(result.returncode))
      print('\n'.join('         ' + line for line in (result.stderr or result.stdout).decode().rsplit('\n', 10)[-10:] if line.strip()))
      # raise Exception('Failed to wget download')
    else:
      csv_file = os.path.join(config.ARCHIVE_DIR, "index.csv")
      web_page.WriteDictToCSV(csv_file, link)

      # Removes first line from file
      CMD2 = [
        *'sed -i 1d'.split(' '),
        link_file,
      ]
      result = run(CMD2, stdout=PIPE, stderr=PIPE, cwd=config.ROOT_FOLDER, timeout=timeout + 1)

  except Exception as e:
    print('       Run to see full output:', 'cd {}; {}'.format(config.ARCHIVE_DIR, ' '.join(CMD)))

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
    fetch_wget(link_info, link_file)
    link_info = grab_link(link_file)