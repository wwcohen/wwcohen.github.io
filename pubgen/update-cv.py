import datetime
import json
import re



def load_pubs_data():
  lines = []
  for line in open('pubs.json'):
    lines.append(line)
  return json.loads("".join(lines))

if __name__ == "__main__":
  pubs = load_pubs_data()
  for pub in pubs:
    if int(pub['year']) >= 2021 and pub['cite'] != "progress":
      a = pub['authors']
      t = pub['title']
      c = pub['cite']
      print(f'{a}. {t}. {c}.')
