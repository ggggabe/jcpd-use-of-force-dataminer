import sys, json, traceback, datetime

from lib.reports import pdf_to_json

if __name__ == '__main__':
  try:
    filename = sys.argv[1]
  except IndexError:
    print('Please specify a Use of Force file.')
    exit()

  incidents_dict = pdf_to_json(filename)     # Figure out memory limit

  with open(filename.replace('pdf', 'json'), 'w+') as outfile:
    json.dump(incidents_dict, outfile, indent=2)
