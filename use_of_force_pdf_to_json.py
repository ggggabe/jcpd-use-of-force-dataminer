import sys, traceback
import traceback
import json

from datetime import datetime
from lib.reports import pdf_to_json

if __name__ == '__main__':
  try:
    filename = sys.argv[1]
  except IndexError:
    print('Please specify a Use of Force file.')
    exit()

  try:
    writefile = sys.argv[2]
  except IndexError:
    print('Error: No filetype specified')
    exit()

  incidents_dict = pdf_to_json(filename)     # Figure out memory limit

  fd = 'json/' + datetime.now().strftime("%m.%d.%Y-%H:%M") + writefile

  print('Writing to ', fd)

  with open(fd, 'w+') as outfile:
    json.dump(incidents_dict, outfile, indent=2)
