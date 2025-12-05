# utilities for planning lectures
#

import argparse
import calendar
import datetime
import fire
import json
import pprint
import re
import os
import yaml

from pydantic import BaseModel, Field

class MonthDate(BaseModel):
    month: int
    date: int
    # computed if we need them
    day_of_week: int = -1
    printable_date: str | None = Field(default=None)

class Config(BaseModel):
    class_num: str
    dates_without_class: list[MonthDate]
    end_date: MonthDate
    lecture_days: list[int]
    start_date: MonthDate
    year: int
    basedir: str = '.'
    schedule_file: str = 'schedule.html'
    schedule_head: str = 'schedule_head.html'
    schedule_foot: str = 'schedule_foot.html'

    def no_class(self, when: MonthDate) -> bool:
        for d in self.dates_without_class:
            if d.month == when.month and d.date == when.date:
                return True
        return False

    def all_lecture_dates(self) -> list[MonthDate]:
        """Generate all days with a lecture.
        """
        result = []
        c = calendar.Calendar(0)   #monday = day index 0
        day_names = "Mon Tue Wed Thu Fri Sat Sun".split()
        month_names = "xx Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split() # cuz start at 1
        start_month, start_date = self.start_date.month, self.start_date.date
        end_month, end_date = self.end_date.month, self.end_date.date
        for month in range(start_month, end_month + 1):
            for (date, day_of_week) in c.itermonthdays2(self.year, month):
                if date <= 0: continue
                if month <= start_month and date < start_date: continue
                if month >= end_month and date > end_date: continue
                if day_of_week not in self.lecture_days: continue
                printable_date = f'{day_names[day_of_week]}  {month_names[month]} {date:2d} {self.year}'
                result.append(MonthDate(month=month, date=date, day_of_week=day_of_week, printable_date=printable_date))
        return result

class SlideDeck(BaseModel):
    summary: str = ''
    links: list[dict[str, str]]

class ContentElement(BaseModel):
    value: str
    deck: SlideDeck | None = Field(default=None)
    kind: str | None = Field(default=None)

class Lecture(BaseModel):
    title: str
    summary: str = ''
    kind: str = Field(default='lecture')
    slide_link: str = ''
    content: list[ContentElement] = Field(default=[])
    status: str = 'not started'
    date: MonthDate | None = Field(default=None)

    def as_str(self):
        """Convert to a quick one-line string view.
        """
        opt_summary = f' - {self.summary}' if self.summary else ''
        opt_date = '??????' if not self.date else self.date.printable_date
        return f'{opt_date:20s} {self.title}{opt_summary} ({self.status})'

    def as_row(self):
        """Convert to a row in an HTML table.
        """
        opt_summary = f' - {self.summary}' if self.summary else ''
        # cols are date, meeting type, title, resources, announcements
        tab = " " * 24
        def make_href(link, text):
            return f'<a href="{link}">{text}</a>' if link else ''
        slide_href = make_href(self.slide_link, ' [Slides]')
        hw_href = '' #for now
        lines = []
        lines.append(f'{" "*20}<tr>')
        lines.append(f'{tab}<td>{self.date.printable_date}</td>')
        lines.append(f'{tab}<td>{self.kind}</td>')
        opt_summary = f' - {self.summary}' if self.summary else ''
        lines.append(f'{tab}<td>{self.title}{opt_summary} {slide_href}</td>')
        lines.append(f'{tab}<td>')
        lines.append(f'{tab}  <ul>')
        for c in self.content:
            if c.deck is not None:
                for d in c.deck.links:
                    for url, text in d.items():
                        lines.append(f'{tab}  <li><a href="{url}">{text}</a>')
        lines.append(f'{tab}  </ul>')
        lines.append(f'{tab}</td>')
        lines.append(f'{tab}<td>{hw_href}</td>')
        lines.append(f'{" "*20}</tr>')
        lines.append(f'{" "*20}<tr>')
        lines.append(f'{" "*20}</tr>')
        return '\n'.join(lines) + '\n'

########## i/o

def load_yaml(filename):
    with open(filename) as fp:
        return yaml.full_load(fp)

def join_lecture_dates(lectures, config):
    """Add all the dates to lectures.
    """
    for lec, md in zip(lectures, config.all_lecture_dates()):
        lec.date = md
        if config.no_class(lec.date):
            lec.summary = 'class cancelled'

def content_as_str(kind, **kw):
    v = kw.get('value', '')
    match kind:
        case 'comment':
            return v
        case 'assignment':
            return v
        case 'deck':
            title = kw['title']
            filename = kw['filename']
            num_slides = kw['num_slides']
            summary = kw['summary']
            return f'{title} ({num_slides} - {filename}) - {summary}'

def show_content(tab, kind, **kw):
    v = kw.get('value', '')
    tabbing = ' ' * tab
    match kind:
        case 'comment':
            print(f'{tabbing}{v}')
        case 'assignment':
            print(f'{tabbing}{v}')
        case 'deck':
            keys = "title filename summary prereqs taught".split(' ')
            for key in keys:
                if kw[key]:
                    print(f"{tabbing} - {key:10s}:{kw[key]}")


def get_assignments(content, **kw):
    # get a list of assignment lines (which start with '* ' in lectures file)
    hw_contents = [c for c in content if c.get('kind', '') == 'assignment']
    if not hw_contents:
        return None
    else:
        def unstar(val):
            return val[len('* '):] if val.startswith('* ') else val 
        return [unstar(c['value']) for c in hw_contents]

def lecture_with_hw_as_str(**lec_d):
    line1 = lecture_as_str(**lec_d)
    assignments = get_assignments(**lec_d)
    return line1 if assignments is None else f'{line1}\n{" "*18}{", ".join(assignments)}'

def lecture_as_str(title, summary, printable_date, content, **kw):
    num_slides = sum([d.get('num_slides', 0) for d in content])
    with_summary = f' - {summary}' if summary else ''
    return f'{printable_date:17s} {title} ({num_slides} slides){with_summary}'

def show_lecture(title, summary, printable_date, content, **kw):
    print(lecture_as_str(title, summary, printable_date, content, **kw))
    for c in content:
        print(f'  {content_as_str(**c)}')

def lecture_row_as_str(title, summary, printable_date, content, **kw):
    # cols are date, meeting type, title, resources, announcements
    tab = " " * 24
    
    meeting_type = dict(
        recitation='<strong class="label label-red">Recitation</strong>',
        lecture='<strong class="label label-pink">Lecture</strong>')
    assignments = get_assignments(content=content) or ['']
    rsrc_links = dict([it for c in lec_d['content'] for link in c.get('links',[]) for it in link.items()]).items()
    def make_href(link, text):
        if link:
            return f'<a href="{link}">{text}</a>'
        else:
            return ''
    def make_href_for_list_of_texts(link, texts):
        if not texts:
            return ''
        if link:
            texts = [f'<a href="{link}">{texts[0]}</a>'] + texts[1:]
        return '<br/> '.join(texts)
    slide_href = make_href(kw.get('slide_link'), ' [Slides]')
    pptx_href = make_href(kw.get('pptx_link'), ' / Slides (pptx)')
    movie_href = make_href(kw.get('movie_link'), ' / Recording')
    notebook_href = make_href(kw.get('notebook_link'), ' / Notebook')
    hw_href = ''
    lines = []
    lines.append(f'{" "*20}<tr>')
    lines.append(f'{tab}<td>{self.printable_date}</td>')
    lines.append(f'{tab}<td>{self.kind}</td>')
    lines.append(f'{tab}<td>{title} {slide_href}</td>')
    lines.append(f'{tab}<td>')
    lines.append(f'{tab}  <ul>')
    for c in self.content:
        if c.deck is not None:
            for d in c.deck.links:
                for url, text in d.items():
                    lines.append(f'{tab}  <li><a href="{url}">{text}</a>')
    lines.append(f'{tab}  </ul>')
    lines.append(f'{tab}</td>')
    lines.append(f'{tab}<td>{hw_href}</td>')
    lines.append(f'{" "*20}</tr>')
    lines.append(f'{" "*20}<tr>')
    lines.append(f'{" "*20}</tr>')
    return '\n'.join(lines) + '\n'











def class_is_cancelled(month, day, config):
    """Is this class cancelled according to the config file?
    """
    month_day_tup = (month, day)
    for month_day_list in config['DATES_WITH_NO_CLASS']:
        if month_day_tup == tuple(month_day_list):
            return True
    return False

def gen_all_dates(config, cancelled):
    c = calendar.Calendar(0)   #monday = day index 0
    day_names = "Mon Tues Wed Thurs Fri Sat Sun".split()
    month_names = "xx Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    (start_month, start_day) = config['START_DATE']
    (end_month, end_day) = config['END_DATE']
    if config.get('LECTURES_PER_WEEK') == 2:
        offsets = [0,2]
    else:
        offsets = [0,2,4]
    meeting_days = {(config['LECTURE_DAY_OF_WEEK'] + k) for k in offsets}
    for month in range(start_month, end_month + 1):
        for (day, day_of_week) in c.itermonthdays2(config['YEAR'], month):
            if day > 0 and (month > start_month or day >= start_day) and (month < end_month or day <= end_day):
                if class_is_cancelled(month, day, config) == cancelled:
                    if (day_of_week in meeting_days):
                        printable_date = "%s %s %d, %d" % (day_names[day_of_week], month_names[month], day, config['YEAR'])
                        yield dict(numeric_date=(month, day, day_of_week), printable_date=printable_date)


def new_week(last_lec_d, lec_d):
    if last_lec_d is None: return False
    return last_lec_d['numeric_date'][-1] > lec_d['numeric_date'][-1]

def lecture_dates(lecture_data, config):
    """List of dicts with fields numeric_date=(month, day, day_of_
    week), printable_date=string where printable_date is of the form
    "Tues Jul 4", months are 0 <= k < 12, days are 1...31, and
    day_of_week is 0 for Mon, 1 for Tues, etc.

    Dates are limited to those that are valid according to the config
    params of START_DATE, END_DATE, DATES_WITH_NO_CLASS, and
    LECTURE_DAY_OF_WEEK.  LECTURE_DAY_OF_WEEK should be 0 for Mon/Wed
    classes, 1 for Tues/Thus.  START_DATE, END_DATE should be (month,
    day) as integers, eg (1, 13) for Jan 13.
    """
    return list(gen_all_dates(config, cancelled=False))

def add_cancelled_dates(lecture_data, config):
    for date_d in gen_all_dates(config, cancelled=True):
        lecture_data.append(dict(title='NO CLASS', content=[], summary='', **date_d))
    lecture_data.sort(key=lambda lec_d: lec_d['numeric_date'])

def old_main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['html', 'syllabus', 'check', 'calendar', 'next'],
        help="\n".join([
            'html: generate schedule.html;',
            'syllabus: summary of planned lectures;',
            'calendar: shorter summary of planned lectures;',
            'next: syllabus output for next --n lectures'])
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='basic info on dates for the course + html generation')
    parser.add_argument(
        '--lectures',
        default='lectures.yaml',
        help='database of info on each lecture')
    parser.add_argument(
        '--slides',
        default='slides.yaml',
        help='database of info on decks for individual "modules"')
    parser.add_argument(
        '--show_cancelled',
        action='store_true',
        help='show dates of cancelled clsses')
    parser.add_argument(
        '--show_weeks',
        action='store_true',
        help='show dividing lines between weeks')
    parser.add_argument(
        '--n',
        type=int,
        default=1,
        help='with action "next", show next n lectures')
    args = parser.parse_args()

    config = load_any(args.config)
    lecture_data = load_any(args.lectures)
    add_default_values(lecture_data)
    slide_data = load_any(args.slides)
    join_lecture_dates(lecture_data, config)
    if args.show_cancelled:
        add_cancelled_dates(lecture_data, config)
    join_slide_content(lecture_data, slide_data)

    if args.action == 'syllabus':
        for lec_d in lecture_data:
            show_lecture(**lec_d)

    elif args.action == 'next':
        today = datetime.date.today()
        mon, day = today.month, today.day
        k = 0
        for lec_d in lecture_data:
            lmon, lday, _ = lec_d['numeric_date']
            if lmon > mon or (lmon==mon and lday >= day):
                show_lecture(**lec_d)
                k += 1
                if k >= args.n:
                    break
            

    elif args.action == 'check':
        check_constraints(lecture_data)

    elif args.action == 'html':
        schedule_filename = os.path.join(config['BASEDIR'], config['SCHEDULE_FILE'])
        schedule_headname = os.path.join(config['BASEDIR'], config['HEADER'])
        schedule_footname = os.path.join(config['BASEDIR'], config['FOOTER'])
        with open(schedule_filename, 'w') as fp:
            for line in open(schedule_headname):
                fp.write(line)
            for lec_d in lecture_data:
                if 'printable_date' not in lec_d:
                    lec_d['printable_date'] = '?NO DATE - probably too many lectures scheduled'
                fp.write(lecture_row_as_str(**lec_d))
            for line in open(schedule_footname):
                fp.write(line)
        print(f'wrote to {schedule_filename}')

    elif args.action == 'calendar':
        last_lec_d = None
        for lec_d in lecture_data:
            if args.show_weeks and new_week(last_lec_d, lec_d):
                print('-' * 40)
            print(lecture_with_hw_as_str(**lec_d))
            last_lec_d = lec_d

    else:
        raise ValueError(f'wtf is {args.action}')

# initialize

def load_lectures(config_file='config.yaml',
                  lecture_file='lectures.yaml', 
                  slide_file='slides.yaml'):
    config = Config(**load_yaml(config_file))
    lecture_list = load_yaml(lecture_file)
    slide_dict = load_yaml(slide_file)
    lectures = [Lecture(**lec) for lec in lecture_list]
    # add slide and date info to lectures
    for lec in lectures:
        for ce in lec.content:
            if ce.value in slide_dict:
                ce.deck = SlideDeck(**slide_dict[ce.value])
    join_lecture_dates(lectures, config)
    return lectures, config

#
# fire main
#

def syllabus():
    lectures, _ = load_lectures()
    for lec in lectures:
        print(lec.as_str())

def html():
    lectures, config = load_lectures()
    schedule_file = os.path.join(config.basedir, config.schedule_file)
    schedule_head = os.path.join(config.basedir, config.schedule_head)
    schedule_foot = os.path.join(config.basedir, config.schedule_foot)
    with open(schedule_file, 'w') as fp:
        for line in open(schedule_head):
            fp.write(line)
        for lec in lectures:
            fp.write(lec.as_row())
        for line in open(schedule_foot):
            fp.write(line)

if __name__ == '__main__':
    fire.Fire()
