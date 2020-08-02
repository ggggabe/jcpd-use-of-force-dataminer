import re

def extract_firearms(d):
  match = re.search('([A-Za-z]+: ?\d*)', d)
  if not match:
    return None

  keyVal = list(map(lambda x: x.strip(), match.groups()[0].split(':')))

  return [keyVal[0].strip().lower(), number(keyVal[1], int)]

def number(s, t):
  m = re.findall('\d+', s.strip())
  if not m:
    return 0
  return t(m[0])

def time(s):
  return re.search('(\d{2}:\d{2})', s.strip()).groups()[0]

def zipcode(s):
  return re.search('(\d{5})', s).groups()[0]
