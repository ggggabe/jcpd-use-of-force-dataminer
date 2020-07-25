def checkbox_message(checkbox, page, bbox) :
  p = page.crop((checkbox['x0'],  checkbox['top'], bbox[2], checkbox['bottom'] + 4))

  tolerance = 50
  if (p.extract_text().split(' ')[0].lower() == 'other') :
    p = page.crop((checkbox['x0'],  checkbox['top'], bbox[2], bbox[3]))

  return ' '.join(list(map(lambda s: s.strip(), p.extract_text().split('\n'))))

def is_checked(c, p) :
  (r, g, b) = p.crop((c['x0'], c['top'], c['x1'], c['bottom'])).objects['rect'][0]['non_stroking_color']

  return True if r + g + b < 3 else False

def extract_checkboxes(page, bbox) :
  checkboxes = []

  try:
    rects = list(filter(lambda r: r['width'] == r['height'], page.rects))
  except KeyError:
    print('No Checkboxes found')
    rects = []

  for rect in rects:
    if is_checked(rect, page) :
      checkboxes.insert(0, checkbox_message(rect, page, bbox))

  return checkboxes
