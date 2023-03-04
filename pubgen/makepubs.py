import datetime
import json
import re

TOPIC_NAME = dict(
    m='Matching/Data Integration',
    t='Text Categorization',
    x='Info Extraction/Reading/QA',
    l='Topic Modeling',
    g='Learning in Graphs',
    d='Intelligent Tutoring',
    r='Rule Learning',
    c='Collaborative Filtering',
    a='Applications',
    f='Formal Results',
    i='Inductive Logic Programming',
    e='Explanation-Based Learning',
    n='Deep Learning',
    k='Neural Knowledge Representation',
    G='GNAT System',
)
VENUE_TYPE = dict(
    C='Conference',
    J='Journal',
    B='Book',
    W='Workshop',
    O='Oher')

THIS_YEAR = datetime.date.today().year

def load_pubs_data():
  lines = []
  for line in open('pubs.json'):
    lines.append(line)
  return json.loads("".join(lines))

def write_header(fp, title):
  fp.write(f"<html><head><title>{title}</title>\n")
  fp.write("<link rel=\"stylesheet\" type=\"text/css\" href=\"style.css\"/>\n")
  fp.write("</head>\n")
  fp.write(f"<body><h3>{title}</h3>\n")

def write_subheader(fp, subhead):
  fp.write(f"<h3>{subhead}</h3>\n")

def write_footer(fp):
  fp.write("<p align=\"center\">[")
  fp.write("<a href=\"pubs-s.html\">Selected papers</a>")
  fp.write("| By topic:")
  for k1 in sorted(TOPIC_NAME.keys()):
    topic = TOPIC_NAME[k1]
    fp.write(f" <a href=\"pubs-{k1}.html\">{topic}</a>| ")
  fp.write(" By year: <a href=\"pubs.html\">All papers</a>")
  fp.write("]</p>\n")
  fp.write("</body></html>\n")

def hyperlink(href, anchor_text):
  if href.find("http") < 0:
    href = f"postscript/{href}"
  if not href or href.find("DBLP-id")>=0:
    return f"<i>{anchor_text}</i>"
  else:
    return f"<a href=\"{href}\">{anchor_text}</a>"

def write_bib_entry(fp, d):
  auth = d['authors']
  yr = d['year']
  linked_title = hyperlink(d['url'], d['title'])
  cite = d['cite']
  comment = d['comment']
  if comment:
    bibentry = f"{auth} ({yr}): {linked_title} in {cite}.<br><ul><li><font size=-1>{comment}</font></ul>"
  else:
    bibentry = f"{auth} ({yr}): {linked_title} in {cite}."
#  print H " <font size=-1>(Originally published as: ",$earlier{$be},")</font>" if $earlier{$be};
#  fp.write("\n</li>\n")
  fp.write(f"<li>{bibentry}\n</li>\n")

def write_bib(fp, bib_entries):
  fp.write("<ol>\n")
  for d in bib_entries:
    write_bib_entry(fp, d)
  fp.write("</ol>\n")

def filter_bib(bib, lo_year, hi_year, topic_key):
  def good_year(d):
    y = int(d['year'])
    return lo_year <= y and y <= hi_year
  def good_topic(d):
    return not topic_key or topic_key in d['topics']
  return [d for d in bib if (good_year(d) and good_topic(d))]

def run_main():
  bib = load_pubs_data()
  print('loaded', len(bib), 'publications')
  # selected publications
  print('preparing selected pubs bibliography')
  with open('../pubs-s.html', 'w') as fp:
    write_header(fp, "Selected and/or recent papers by William W. Cohen")
    for y in [THIS_YEAR, THIS_YEAR-1, THIS_YEAR-2]:
      print('- recent papers from',y)
      write_subheader(fp, f"Recent papers: {y}")
      write_bib(fp, filter_bib(bib, int(y), int(y), None))
    print('- other selected papers')
    write_subheader(fp, "Selected other papers")
    write_bib(fp, filter_bib(bib, 0, THIS_YEAR-3, 's'))
    write_footer(fp)
  # by topic
  for k in TOPIC_NAME.keys():
    topic = TOPIC_NAME[k]
    print('preparing topic bibliography for', topic)
    with open(f"../pubs-{k}.html", 'w') as fp:
      write_header(fp, f"William W. Cohen's Papers: {topic}")
      write_bib(fp, filter_bib(bib, 0, 9999, k))
      write_footer(fp)
  # all by year
  print('preparing by-year bibliography')
  years = set([d.get('year') for d in bib])
  with open("../pubs.html", "w") as fp:
    write_header(fp, "Papers by William W. Cohen")
    for y in sorted(list(years), reverse=True):
      write_subheader(fp, f"Papers published in {y}")
      write_bib(fp, filter_bib(bib, int(y), int(y), None))
    write_footer(fp)

if __name__ == "__main__":
  run_main()
