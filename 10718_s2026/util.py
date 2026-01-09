# utilities for planning lectures
#

import calendar
import fire
import os
import yaml

from pydantic import BaseModel, Field

class MonthDate(BaseModel):
    """A date with month and day of month (date).
    """
    month: int
    date: int
    # computed if we need them
    day_of_week: int = -1
    week_num: int = -1
    def as_str(self, show_week_num=False):
        day_names = "Mon Tue Wed Thu Fri Sat Sun".split()
        month_names = "xx Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split() # cuz start at 1
        opt_week_num = 'f{self.week_num:2d} ' if show_week_num else ''
        return f'{opt_week_num}{day_names[self.day_of_week]}  {month_names[self.month]} {self.date:2d}'

class Config(BaseModel):
    """Configure a class
    """
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
        start_month, start_date = self.start_date.month, self.start_date.date
        end_month, end_date = self.end_date.month, self.end_date.date
        week_num = 0
        for month in range(start_month, end_month + 1):
            for (date, day_of_week) in c.itermonthdays2(self.year, month):
                if date <= 0: continue
                if month <= start_month and date < start_date: continue
                if month >= end_month and date > end_date: continue
                if day_of_week == 0:
                    week_num += 1
                if day_of_week not in self.lecture_days: continue
                result.append(
                    MonthDate(month=month, date=date, day_of_week=day_of_week, week_num=week_num))
        return result

class SlideDeck(BaseModel):
    """Info about a slide deck.
    """
    summary: str = ''
    links: list[dict[str, str]]

class ContentElement(BaseModel):
    """A content element for a lecture.
    """
    deck_tag: str | None = None
    form: str | None = None
    deadline: str | None = None
    # a computed field
    deck: SlideDeck | None = None

class Lecture(BaseModel):
    title: str
    summary: str = ''
    kind: str = Field(default='lecture')
    slide_link: str = ''
    readings: list[dict[str, str]] = []
    # slide deck contents - for resources, and me
    content: list[ContentElement] = Field(default=[])
    # computed date
    date: MonthDate | None = Field(default=None)
    status: str = 'not started'  # for me only

    def as_str(self):
        """Convert to a quick one-line string view.
        """
        opt_summary = f' - {self.summary}' if self.summary else ''
        opt_date = '??????' if not self.date else self.date.as_str()
        return f'{opt_date:20s} {self.title}{opt_summary} ({self.status})'

    def as_openable_list(self, tab, summary, url_text_pairs):
        lines = []
        if url_text_pairs:
            lines.append(f'{tab}<details><summary style="color:SteelBlue;text-decoration: underline;">{summary}</summary>')
            lines.append(f'{tab}  <ul>')
            for url, text in url_text_pairs:
                if url is not None:
                    lines.append(f'{tab}  <li><a href="{url}">{text}</a>')
                else:
                    lines.append(f'{tab}  <li>{text}')
            lines.append(f'{tab}  </ul>')
            lines.append(f'{tab}  </details>')
        return lines

    def as_row(self):
        """Convert to a row in an HTML table.
        """
        opt_summary = f' - {self.summary}' if self.summary else ''
        # cols are week, date, meeting type, title, resources, announcements
        tab = " " * 24
        def make_href(link, text):
            return f'<a href="{link}">{text}</a>' if link else ''
        slide_href = make_href(self.slide_link, ' [Slides]')
        hw_href = '' #for now
        lines = []
        lines.append(f'{" "*20}<tr>')
        try:
            # week
            lines.append(f'{tab}<td>{self.date.week_num}</td>')
            # date
            lines.append(f'{tab}<td>{self.date.as_str(show_week_num=False)}</td>')
        except AttributeError:
            lines.append(f'{tab}<td>??</td><td>no date?</td>')
        # meeting type
        lines.append(f'{tab}<td>{self.kind}</td>')
        # title [- summary]
        opt_summary = f' - {self.summary}' if self.summary else ''
        lines.append(f'{tab}<td>{self.title}{opt_summary} {slide_href}</td>')
        # resources
        lines.append(f'{tab}<td>')
        resources = [
            url_text_pair
            for c in self.content if c.deck is not None
            for d in c.deck.links
            for url_text_pair in d.items()]
        lines.extend(self.as_openable_list(tab, 'Optional readings', resources))
        lines.append(f'{tab}</td>')
        # announcements
        lines.append(f'{tab}<td>')
        deadlines = [(None, c.deadline) for c in self.content if c.deadline]
        lines.extend(self.as_openable_list(tab, 'Deadlines', deadlines))
        readings = [
            url_text_pair for d in self.readings
            for url_text_pair in d.items()]
        readings.extend([(c.form, 'Give feedback') for c in self.content if c.form])
        lines.extend(self.as_openable_list(tab, 'Required readings/feedback', readings))
        lines.append(f'{tab}</td>')
        # close row
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
            lec.summary = 'no class'

# initialize

def load_lectures(config_file='config.yaml',
                  lecture_file='lectures.yaml', 
                  slide_file='slides.yaml'):
    config = Config(**load_yaml(config_file))
    lecture_list = load_yaml(lecture_file)
    slide_dict = load_yaml(slide_file)
    lectures = [Lecture(**lec) for lec in lecture_list]
    # pull in slide-deck information for ContentElements
    for lec in lectures:
        for ce in lec.content:
            if ce.deck_tag in slide_dict:
                ce.deck = SlideDeck(**slide_dict[ce.deck_tag])
    join_lecture_dates(lectures, config)
    return lectures, config

#
# fire mains
#

class FireMain:

    def syllabus(self):
        lectures, _ = load_lectures()
        for lec in lectures:
            print(lec.as_str())

    def html(self):
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
    fire.Fire(FireMain)
    
