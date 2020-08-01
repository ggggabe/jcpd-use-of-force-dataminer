import sys, traceback
import traceback
import json

from lib.reports import pdf_to_json

testfile = 'jcpd_cut.pdf'
fullfile = 'jcpd_force_2019.pdf'
resultsfile = 'logs/test.log'
resultsfullfile = 'logs/full.log'

test_pages= [
  (632, 633)

  #(95,97),
  #(9, 12),
  #(15, 17),
  #(40, 42),
  #(1, 8)
]

if __name__ == '__main__':
  results = []

  for pages in test_pages:
    result = pdf_to_json(fullfile, pages)
    results.append(result)

  with open(resultsfile, 'w+') as outfile:
    json.dump(results, outfile, indent=2)
