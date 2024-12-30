import datetime
import json
import re

def load_pubs_data():
  lines = []
  for line in open('pubs.json'):
    lines.append(line)
  return json.loads("".join(lines))

mapping_str="""Bhuwan Dhingra	Google/Duke
Bill Yuchen Lin	Google/USC
Danish Pruthi	Google/CMU
Einat Minkov	Google/Univ. Haifa
Fan Yang	CMU
Fei Sha	Google/USC
Graham Neubig	CMU
Haitian Sun	Google/CMU
Hannaneh Hajishirzi	Univ. Wash
Kathryn Rivard Mazaitis	CMU
Ruslan Salakhutdinov	CMU
Siddhant Arora	CMU
Taylor Berg-Kirkpatrick	UCSD
Vidhisha Balachandran	CMU
Wenhu Chen	Google/Univ. Waterloo
William Wang	UCSB
Xiang Ren	USC
Xinghua Lu	U.Pitt
Xinyi Wang	UCSB
Yulia Tsvetkov	Univ. Wash
Zachary C. Lipton	CMU"""

mapping = dict(line.split("\t") for line in mapping_str.split("\n"))

def run_main():
  bib_entries = load_pubs_data()
  latest = {}
  for d in bib_entries:
      d['year'] = int(d['year'])
      if d['year'] >= 2020:
          authors = re.split('(\s*,\s*|\s+and\s+)', d['authors'])
          for a in authors:
              if a not in latest:
                  latest[a] = d['year']
              latest[a] = max(d['year'], latest[a])
  droppers = []
  for a in list(latest):
      if a.startswith('and '):
          droppers.append(a)
          latest[a[4:]] = latest[a]
  for d in droppers:
      del latest[d]
  del latest[' and ']
  del latest[', ']
  del latest['William Cohen']
  del latest['William W. Cohen']
  for a in sorted(list(latest)):
      affil = mapping.get(a, 'Google')
      print(f'{a}\t{affil}\t\t{latest[a]}')

if __name__ == "__main__":
  run_main()
