import sys, traceback
import pdfplumber
import traceback
import json
from datetime import datetime

GROUPS = [
  {
    'label': 'type',
    'width': 100
  },
  {
    'label': 'meta',
    'width': 200
  },
  {
    'label': 'subject',
    'width': 240
  },
  {
    'label': 'force',
    'width': 130
  },
  {
    'label': 'firearmsDischarge',
    'width': 80
  }
]

def _exit():
  print ('exiting')
  exit()

def readable(page):
  try:
    title = ' '.join(page.crop((100, 20, page.width - 100, 60)).extract_text().split('\n'))
  except Exception:
    title = page.crop((0, 0, 100, 30)).extract_text()

    if (title == None) :
      return False

  return True

def extract_checkboxes(page, message_width) :
  checkboxes = []

  try:
    rects = list(filter(lambda r: r['width'] == r['height'], page.rects))
  except KeyError:
    print('No Checkboxes found')
    rects = []

  for rect in rects:
    if is_checked(rect, page) :
      checkboxes.insert(0, checkbox_message(rect, page, message_width))

  return checkboxes

def checkbox_message(checkbox, page, width) :
  p = page.crop((checkbox['x0'],  checkbox['top'], checkbox['x1'] + width, checkbox['bottom'] + 4))

  tolerance = 50
  if (p.extract_text().split(' ')[0].lower() == 'other') :
    p = page.crop((checkbox['x0'],  checkbox['top'], checkbox['x1'] + width, checkbox['bottom'] + tolerance))

  return ' '.join(list(map(lambda s: s.strip(), p.extract_text().split('\n'))))

def is_checked(c, p) :
  (r, g, b) = p.crop((c['x0'], c['top'], c['x1'], c['bottom'])).objects['rect'][0]['non_stroking_color']

  return True if r + g + b < 3 else False


LR_MARGIN = 24
SECTION_MARGIN = 20

A_TOP = 60
A_SIZE = 100

B_TOP = A_TOP + A_SIZE + SECTION_MARGIN
B_SIZE = 70

C_TOP = B_TOP + B_SIZE + SECTION_MARGIN
C_SIZE = 280

def get_bboxes(p):
  return sorted(list(filter(lambda r: r['width'] > p.width - 200 and r['height'] < 2, p.rects)), key=lambda s: s['top'])

# :::: EXTRACT INCIDENT INFORMATION :::: #
# In place add keys from page `p` to the blob `b` containing incident information
def get_incident(b, p):
  bboxes = get_bboxes(p)
  if not 'incident' in b.keys() :
    b['incident'] = {}

  a_section = p.crop((
    bboxes[1]['x0'],
    bboxes[1]['top'],
    bboxes[1]['x1'],
    bboxes[1]['bottom'] + 50
  ))

  b['incident']['type'] = extract_checkboxes(a_section, 100)

  lines = a_section.extract_text().split('\n')
  columns = list(map(lambda s: s.lower(), lines[0].split(' ')))

  keys = list(map(lambda s: s.lower(), columns[:3] + ['location', 'incident_number']))
  vals = list(filter(lambda v: len(v) > 0, lines[1].split(' ')))

  for (key, value) in list(zip(keys, vals[:2] + [vals[3]] + [lines[2]] + [vals[-1]])) :
    b['incident'][key] = value

  b['incident']['location'] = ' '.join(list(filter(lambda s: len(s), list(map(lambda s: s.strip(), p.within_bbox((LR_MARGIN + 230, A_TOP + 30, LR_MARGIN + 400, A_TOP + 80)).extract_text().split('\n'))))))

# :::: EXTRACT OFFICER INFORMATION :::: #
# In place add keys from page `p` to the blob `b` containing officer information
def get_officer(b, p):
  bboxes = get_bboxes(p)
  (fired, hits) = tuple(p.within_bbox((
    bboxes[4]['x1'] - 30 ,
    bboxes[4]['top'] + 110,
    bboxes[4]['x1'] - 10,
    bboxes[4]['top'] + 140
  )).extract_text().split('\n'))

  b['officer'] = {
    'force': extract_checkboxes(p.crop((p.width/2, C_TOP + 100, p.width - LR_MARGIN - 120, C_TOP + 240)), 120),
    'firearmsDischarge': {
      'intent': extract_checkboxes(p.crop((p.width*3/4, C_TOP + 100, p.width - LR_MARGIN, C_TOP + 180)), 120),
      'fired': int(fired),
      'hits': int(hits)
    }
  }

  lines = p.crop((
    bboxes[3]['x0'],
    bboxes[3]['top'],
    bboxes[3]['x1'],
    bboxes[3]['bottom'] + 50
  )).extract_text().split('\n')
  (columns, vals) = (lines[0].split(' '), lines[1].split(' '))

  keys = [columns[0]] + [columns[4]] + columns[-5:]

  for (key, value) in list(zip(keys, [' '.join(vals[:-6])] + vals[-6:])) :
    b['officer'][key.lower()] = value

# :::: EXTRACT OFFICER INFORMATION :::: #
# In place add keys from page `p` to the blob `b` containing subject information
def get_subject(b, p) :
  bboxes = get_bboxes(p)

  b['subject'] = {
    'actions': extract_checkboxes(p.crop((
      LR_MARGIN,
      C_TOP + 80,
      p.width/2 - 10,
      C_TOP + C_SIZE - 30
    )), 280)
  }

  info = p.crop((bboxes[4]['x1'] - 260, bboxes[4]['top'], bboxes[4]['x1'], bboxes[4]['top'] + 30)).extract_text().split('\n')
  arrested = p.crop((bboxes[4]['x1'] - 260, bboxes[4]['top'] + 30, bboxes[4]['x1'] - 190, bboxes[4]['top'] + 60)).extract_text().split('\n')
  charges = p.crop((bboxes[4]['x1'] - 180, bboxes[4]['top'] + 30, bboxes[4]['x1'], bboxes[4]['top'] + 70)).extract_text().split('\n')

  i = 0
  info_labels = info[0].split(' ')
  info_values = info[1].split(' ')
  initial_length = len(info_values)

  while i < len(info_labels) - initial_length :
    info_values = ['REDACTED'] + info_values
    i += 1

  for (k, v) in list(zip(
    info_labels + [arrested[0], charges[0]],
    info_values + [arrested[1], ("yes" if len(charges) == 2 else "None")]
  )):
    b['subject'][k.lower()] = v

def pdfToJson(f) :
  pdf = pdfplumber.open(f)
  incidents = []
  failed = []

  for page in pdf.pages:
    sys.stdout.write('\r Page {} of {}'.format(page.page_number, len(pdf.pages)))
    if not readable(page) :
      print('\nEncountered scannedpdf, skipping...')
      failed.append(page.page_number)
      continue

    blob = {
      'page': page.page_number,
      'incident': {},
      'subject': {},
    }

    try :
      get_incident(blob, page)
    except Exception as e:
      traceback.print_tb(e.__traceback__, file=sys.stdout)
      failed.append(page.page_number)
      print('Error <get_incident> (', page.page_number, '): ', e)

      continue

    try :
      get_officer(blob, page)
    except Exception as e:
      traceback.print_tb(e.__traceback__, file=sys.stdout)
      failed.append(page.page_number)
      print('Error <get_officer> (', page.page_number, '): ', e)

      continue

    try :
      get_subject(blob, page)
    except Exception as e:
      traceback.print_tb(e.__traceback__, file=sys.stdout)
      failed.append(page.page_number)
      print('Error <get_subject>(', page.page_number, '): ', e)

      continue

    incidents.append(blob)

  f = 'json/' + datetime.now().strftime("%m.%d.%Y-%H:%M:%S") + '-use-of-force.json'

  with open(f, 'w+') as outfile:
    json.dump(incidents, outfile)

  print('Completed {} of {}'.format(len(incidents), len(pdf.pages)))
  print('Failed: {}'.format(failed))
  print('saved output to ' + f)

if __name__ == '__main__':
  try:
    filename = sys.argv[1]
  except IndexError:
    print('Error: No filetype specified')
    _exit()

  pdfToJson(filename)
