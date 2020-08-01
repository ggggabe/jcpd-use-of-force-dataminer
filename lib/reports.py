import pdfplumber, sys, traceback, json, os
import re

from .page import Page

class Incident:
  def __init__(self, leaf):
    sections = []
    self.id = None
    self.officers = {}
    self.subjects = []
    self.signatures = []
    self.pages = []
    self.zip = ''

    for page in leaf:
      for s in page.sections:
        self.add_section(s)

  def json(self):
    return {
      'id': self.id,
      'pages': self.pages,
      'time': self.time,
      'date': self.date,
      'day': self.day,
      'location': self.location,
      'zip': self.zip,
      'type': self.type,
      'signatures': self.signatures,
      'officers': self.officers,
      'subjects': self.subjects
    }

  def merge_incident(self, i):
    self.pages = self.pages + i.pages

    for o_key in i.officers.keys():
      if o_key == 'unkown':
        print('unknown officer')
        continue

      if o_key not in self.officers.keys():
        self.officers[o_key] = i.officers[o_key]

    self.subjects = self.subjects + i.subjects

  def add_section(self, s):
    if s.type == 'A':
      self.add_incident(s)
    elif s.type == 'B':
      self.add_officer(s)
    elif s.type == 'C':
      self.add_subject(s)
    elif s.type == 'S':
      self.add_signature(s)
    else:
      print('Unkown Section' + str(s.page.page_number))


  def add_incident(self, s):
    self.id = s.data['INCIDENT NUMBER'].strip()
    self.time = re.search('(\d{2}:\d{2})', s.data['Time'].strip()).groups()[0]
    self.date = s.data['Date'].strip()
    self.day = s.data['Day of Week'].strip()
    self.location = s.data['Location'].strip()
    self.zip = re.search('(\d{5})', self.location).groups()[0]
    self.type = s.data['Type of Incident'] if isinstance(s.data['Type of Incident'], list) else []
    self.pages.append(s.page.page_number)

  def add_officer(self, s):
    keys = s.data.keys()
    officer = {
      'name': s.data['Name (Last, First, Middle)'] if 'Name (Last, First, Middle)' in keys else None,
      'badge': s.data['Badge #'] if 'Badge #' in keys else None,
      'sex': s.data['Sex'] if 'Sex' in keys else None,
      'race': s.data['Race'] if 'Race' in keys else None,
      'age': int(s.data['Age']) if 'Age' in keys else None,
      'injured': bool(s.data['Injured'] == 'Yes') if 'Injured' in keys else False,
      'killed': bool(s.data['Killed'] == 'Yes') if 'Killed' in keys else False,
      'rank': str(s.data['Rank']) if 'Rank' in keys else None,
      'duty': s.data['Duty Assignment'] if 'Duty Assignment' in keys else None,
      'service_years': int(s.data['Years of Service']) if 'Years of Service' in keys else None,
    }

    if officer['badge']:
      self.officers[officer['badge']] = officer
    else:
      self.officers['unknown'].append(officer)

  def add_subject(self, s):
    keys = s.data.keys()
    subject = {
      'id': '{}-{}{}'.format(s.page.page_number, s.type, s.type_index),
      'age': int(s.data['Age']) if 'Age' in keys and len(s.data['Age']) else None,
      'weapon': True if 'Weapon' in keys and s.data['Weapon'] == 'Yes' else False,
      'injured': True if 'Injured' in keys and s.data['Injured'] == 'Yes' else False,
      'killed': True if 'Killed' in keys and s.data['Killed'] == 'Yes' else False,
      'arrested': True if 'Arrested' in keys and s.data['Arrested'] == 'Yes' else False
    }

    keyMaps = [
      ('actions', "Subject\u2019s Actions (check all that apply)", list),
      ('force_received', "Officer\u2019s Use of force toward this subject", list),
      ('meta', 'meta', None),
      ('sex', 'Sex', None),
      ('race', 'Race', None),
      ('charges', 'Charges', None),
    ]

    for (s_key, d_key, d_type) in keyMaps:
      if d_key in keys:
        if not d_type or isinstance(s.data[d_key], d_type):
          subject[s_key] = s.data[d_key]
        else:
          subject[s_key] = None

    if (len(subject['charges'])):
      subject['charges'] = list(map(lambda c: c.strip().upper(), subject['charges'].split(',')))

    self.subjects.append(subject)

  def add_signature(self, s):
    signature = {}
    keyMaps = [
        ('officer_signature', 'Signature:'),
        ('officer_sign_date', 'Date:'),
        ('officer_sign_date', 'Date:'),
        ('supervisor_name', 'Print Supervisor Name:'),
        ('supervisor_signature', 'Supervisor Signature:')
    ]

    d_keys = s.data.keys()

    for (s_key, d_key) in keyMaps:
      if d_key in d_keys:
        signature[s_key] = s.data[d_key]

    self.signatures.append(signature)

def add_incident_to_dict(d, i):
  if i.id in d.keys():
    d[i.id].merge_incident(i)
    return

  d[i.id] = i

def pdf_to_json(filename, interval = None):
  pdf = pdfplumber.open(filename)
  pages = pdf.pages

  if interval :
    (start_page, end_page) = interval
    start_page -= 1

    if (end_page == len(pages)):
      pages = pages[start_page:]
    else :
      pages = pages[start_page: end_page]

  skipped = []
  leaf = []
  incidentsDict = {}

  i = 1
  max_i = len(pages)

  for page in pages:
    sys.stdout.write('\r {} of {} '.format(i, max_i))
    i += 1
    p = Page(page)

    if p.report_start :
      if len(leaf):
        incident = Incident(leaf)
        add_incident_to_dict(incidentsDict, incident)

      leaf = [p]
      continue

    if not p.has_content:
      skipped.append(p.page_number)
      continue

    leaf.append(p)


  if len(leaf):
    incident = Incident(leaf)
    add_incident_to_dict(incidentsDict, incident)

  if len(skipped) :
    logpath = 'logs/skipped.json'
    write_opt = 'a'

    if not os.path.exists(logpath) :
      write_opt = 'w+'

    with open(logpath, write_opt) as log:
      print('Failed some.')
      json.dump(skipped, log, indent=2)

  for key in incidentsDict.keys():
    incidentsDict[key] = incidentsDict[key].json()

  return incidentsDict
