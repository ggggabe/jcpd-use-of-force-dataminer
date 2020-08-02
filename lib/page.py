import traceback, re
import json
from .checkboxes import extract_checkboxes
from .clean import extract_firearms

class Row:
  tolerance = 3
  firstwordX = 32

  def __init__(self, bbox, page):
    self.page = page.within_bbox(bbox)
    self.bbox = bbox

    cells = []
    col_x = 0
    prev_x = 0

    firstword = True

    for word in list(sorted(self.page.crop((bbox[0], bbox[1], bbox[2], bbox[1] + 10)).extract_words(), key=lambda b: b['x0'])):
      if word['text'] == 'Under':
        word['x0'] = self.firstwordX

      firstword = False

      if word['x0'] - prev_x > self.tolerance:
        cells.append((col_x, bbox[1], word['x0'] - self.tolerance, bbox[3]))
        col_x = word['x0'] - self.tolerance

      prev_x = word['x1']

    cells.append((col_x, bbox[1], bbox[2], bbox[3]))
    self.cells = cells[1:]

class Section:
  def __init__(self, header, bbox, page):
    type_substr = header.split()[0]
    ti = type_substr[1:type_substr.find('.')]

    self.page = page.within_bbox(bbox)
    self.type = type_substr[0]
    self.type_index = ti if len(ti) else 0
    self.header = header[header.find('.') + 1:].strip()
    self.bbox = bbox
    self.field = self.header.split()[0].lower()
    self.cells = []
    self.data = {}

    self.__init_cells()


  def __init_cells(self):
    linebreaks = sorted(list(set(map(lambda r: r['bottom'], list(filter(lambda h: h['width'] > 40 and (h['height'] == .750 or h['height'] == 1.500) , self.page.rects))))))
    i = 0

    for i in range(len(linebreaks) - 1):
      row = Row((self.bbox[0], linebreaks[i], self.bbox[2], linebreaks[i+1]), self.page)

      for cell in list(sorted(row.cells, key=lambda x: x[0])):
        c = self.page.crop(cell)

        if self.type == 'A':
          i += 1

        cell_text = c.extract_text()
        data = cell_text.split('\n')

        if len(list(filter(lambda r: r['height'] == r['width'], c.rects))) :
          if (data[0] == 'Under the influence') :
            data[0] = 'meta'

          self.data[data[0]] = extract_checkboxes(c, self.bbox)

          if data[0] == 'Firearms Discharge':
            self.data[data[0]] = {
              'checkboxes': self.data[data[0]]
            }

            print('data: ')
            print(data)
            for d in data:
              a = extract_firearms(d)

              if not a:
                continue

              (key, val) = a

              self.data[data[0]][key] = val
        else:
          self.data[data[0]] = ''.join(data[1:]) if len(data) else None

      self.cells = self.cells + row.cells

  def json(self):
    return {
      'type': self.type,
      'type_index': self.type_index,
      'header': self.header,
      'bbox': self.bbox,
      'field': self.field
    }

class Page:
  tolerance=3

  def __init__(self, page) :
    self.page = page
    self.page_number = page.page_number
    self.header = None
    self.has_content = page.extract_text() != None
    self.header_text = None

    if self.has_content:
      self.extract_header_text()


  def extract_header_text(self):

    # Extract Header Text to classify doc type
    if len(self.page.rects) > 0:
      header = self.page.within_bbox((0, 0, self.page.width, sorted(self.page.rects, key=lambda r: r['bottom'])[0]['bottom'] + self.tolerance)).extract_words()
      self.header = header
      self.header_text = ' '.join(list(map(lambda h: h['text'], header)))

    self.report_start = self.header_text == 'JERSEY CITY POLICE DEPARTMENT USE OF FORCE REPORT'
    self.sections = self.get_sections()

  def get_sections(self):
    if (self.header_text == 'If this officer used force against more than two subjects in this incident, attach additional USE OF FORCE REPORTS') :
      #then it only has a sig on it
      headers = [{
        'top': self.header[0]['top'],
        'val': 'Signature'
      }]
    else:
      headers = self.grab_headers()

    sectionBreaks = sorted(list(map(lambda h: h['top'], headers)) + [self.page.height])
    sections = []

    for i in range(len(headers)):
      sections.append(Section(headers[i]['val'], (
        0,
        sectionBreaks[i] - 3,
        self.page.width,
        sectionBreaks[i + 1] - 30),
        self.page
      ))

    return sections

  def grab_headers(self):
    linebreaks = sorted(list(map(lambda r: r['bottom'], list(filter(lambda h: h['height'] == 1.500, self.page.rects)))))
    if self.report_start:
      linebreaks = linebreaks[1:]

    headers = []

    for linebreak in linebreaks:
      page = self.page.within_bbox((0, linebreak - 40, self.page.width, linebreak))

      maxSize = 0

      for char in page.chars:
        if char['size'] > maxSize:
          maxSize = char['size']

      headerChars = []

      for char in list(filter(lambda c: c['size'] == maxSize, page.chars)):
        headerChars.append(char)

      if len(headerChars) :
        val = ''.join(list(map(lambda c: c['text'], headerChars)))

        if val == 'If this officer used force against more than two subjects in this incident, attach additional USE OF FORCE REPORTS':
          val = 'Signature'

        headers.append({
          'top': linebreak,
          'val': val
        })

    return headers
