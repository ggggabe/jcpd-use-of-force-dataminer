import re

def number(s, t):
  m = re.findall('\d+', s)
  return t(m[0])

def time(s):
  return re.search('(\d{2}:\d{2})', s.strip()).groups()[0]

def zip(s):
  return ee.search('(\d{5})', s).groups()[0]
