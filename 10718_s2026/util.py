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
        some_resources = False
        for c in self.content:
            if c.deck is not None:
                for d in c.deck.links:
                    for url, text in d.items():
                        if not some_resources:
                            some_resources = True
                            lines.append(f'{tab}<details><summary style="color:SteelBlue;text-decoration: underline;">Resources</strong></summary>')
                            lines.append(f'{tab}  <ul>')
                        lines.append(f'{tab}  <li><a href="{url}">{text}</a>')
        if some_resources:
            lines.append(f'{tab}  </ul>')
            lines.append(f'{tab}  </details>')
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
