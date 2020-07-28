import pdfplumber
import traceback
import json
import os

from .page import Page

class Incident:
  def __init__(self, leaf):
    sections = []
    self.id = None
    self.officers = {'unknown': []}
    self.subjects = []
    self.signatures = []
    self.pages = []

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
      'type': self.type,
      'signature': self.signatures,
      'officers': self.officers,
      'subjects': self.subjects
    }

  def merge_incident(self, i):
    self.pages = self.pages + i.pages

    for o_key in i.officers.keys():
      if o_key == 'unkown':
        self.officers['unkown'] = self.officers['unknown'] + i.officers[o_key]
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
    self.id = s.data['INCIDENT NUMBER']
    self.time = s.data['Time']
    self.date = s.data['Date']
    self.day = s.data['Day of Week']
    self.location = s.data['Location']
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
      'injured': bool(s.data['Injured']) if 'Injured' in keys else False,
      'killed': bool(s.data['Killed']) if 'Killed' in keys else False,
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
    self.subjects.append({
      'id': '{}-{}{}'.format(s.page.page_number, s.type, s.type_index),
      'sex': s.data['Sex'] if 'Sex' in keys else None,
      'race': s.data['Race'] if 'Race' in keys else None,
      'age': int(s.data['Age']) if 'Age' in keys and len(s.data['Age']) else None,
      'weapon': True if 'Weapon' in keys and s.data['Weapon'] == 'Yes' else False,
      'injured': True if 'Injured' in keys and s.data['Injured'] == 'Yes' else False,
      'killed': True if 'Killed' in keys and s.data['Killed'] == 'Yes' else False,
      'arrested': True if 'Arrested' in keys and s.data['Arrested'] == 'Yes' else False,
      'charges': s.data['Charges'],
      'actions': s.data["Subject\u2019s Actions (check all that apply)"] if isinstance(s.data["Subject\u2019s Actions (check all that apply)"], list) else [],
      'force_received': s.data["Officer\u2019s Use of force toward this subject"] if isinstance(s.data["Officer\u2019s Use of force toward this subject"], list) else []
    })

  def add_signature(self, s):
    self.signatures.append({
      'officer_signature': s.data['Signature:'],
      'officer_sign_date': s.data['Date:'],
      'supervisor_name': s.data['Print Supervisor Name:'],
      'supervisor_signature': s.data['Supervisor Signature:']
    })

class ShotReport:
  intentional = None
  fired = 0
  hits = 0

  def __init__(self, params):
    keys = params.keys()

    if 'intent' in keys:
      self.intent = params['intent']

    if 'fired' in keys:
      self.fired = params['fired']

    if 'hits' in keys:
      self.hits = params['hits']

class Officer:
  force = []
  brutalized = []

  name = None
  badge = None
  sex = None
  race = None
  age = None
  injured = None
  killed = None

  def __init__(self, params):
    keys = params.keys()

    if 'subjects' in keys:
      self.add_victims(params['subjects'])    #expects Array<Subjects>

    if 'name' in keys:
      self.name = params['name']

    if 'badge' in keys:
      self.badge = params['badge']

    if 'sex' in keys:
      self.sex = params['sex']

    if 'race' in keys:
      self.race = params['race']

    if 'age' in keys:
      self.age = params['age']

    if 'injured' in keys:
      self.injured = params['injured']

    if 'killed' in keys:
      self.killed = params['killed']

  def add_victims(self, victims):
    self.brutalized = self.brutalized + victims


class Subject:
  actions = []
  charges = []

  force_experienced = []
  shot_report = None

  name = None
  race = None
  sex = None
  age = None
  weapon = None

  injured = None
  killed = None

  arrested = None

  def __init__(self, params):
    keys = params.keys()

    if 'actions' in keys:
      self.actions = params['actions']   #expects Array<String>

    if 'charges' in keys:
      self.charges = params['charges']   #expects Array<String>

    if 'force' in keys:
      self.force_experienced = params['force']

    if 'name' in keys:
      self.name = params['name']

    if 'race' in keys:
      self.race = params['race']

    if 'sex' in keys:
      self.sex = params['sex']

    if 'age' in keys:
      self.age = params['age']

    if 'weapon' in keys:
      self.weapon = params['weapon']

    if 'injured' in keys:
      self.injured = params['injured']

    if 'killed' in keys:
      self.killed = params['killed']

    if 'arrested' in keys:
      self.arrested = params['arrested']

class IncidentReport:
  subjects = []
  officers = []

  def __init__(self, pages): # i should be the first page of the report
    self.type = p['type']
    self.date = p['date']
    self.time = p['time']
    self.day = p['day']
    self.location = p['location'].strip()
    self.id = p['incident_number']

  def add_subject(self, s):
    self.subjects.append(Subject(s))

  def add_officer(self, o):
    o.addIncident(self.incident.id)
    self.officers.append(o)

def add_incident_to_list(l, i):
  l.append(i.json())

def add_incident_to_dict(d, i):
  if i.id in d.keys():
    d[i.id].merge_incident(i)
    return

  d[i.id] = i

def pdf_to_json(filename):
  pdf = pdfplumber.open(filename)

  #pages = pdf.pages[95:97]
  #pages = pdf.pages[9:12]
  pages = pdf.pages[26:28]
  #pages = pdf.pages[:8]

  skipped = []
  leaf = []
  incidentsList = []
  incidentsDict = {}


  i = len(pages)

  for page in pages:
    i += 1
    p = Page(page)

    if p.report_start :
      if len(leaf):
        incident = Incident(leaf)
        add_incident_to_dict(incidentsDict, incident)
        add_incident_to_list(incidentsList, incident)

      leaf = [p]
      continue

    if not p.has_content:
      skipped.append(p.page_number)
      continue

    leaf.append(p)

    sys.stdout.write('\r Page {} of {}'.format(page.page_number, i))

  if len(leaf):
    incident = Incident(leaf)
    add_incident_to_dict(incidentsDict, incident)
    add_incident_to_list(incidentsList, incident)

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

  return (incidentsList, incidentsDict)
