from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import datetime
import re


class TimetableClient:

    def __init__(self, driver_path):
        options = Options()
        options.add_argument("--headless")

        self.browser = Chrome(driver_path, options=options)

    def get_timetable(self, url):
        self.browser.get(url)
        self.browser.switch_to.frame(self.browser.find_element_by_css_selector('iframe:first-child'))

        week_num = self.browser.find_element_by_css_selector('#wkSelList').get_attribute("value")
        start_date = self.browser.find_element_by_css_selector(f'#wkSelList option[value="{week_num}"]')\
            .get_attribute('id')

        days = self.browser.find_elements_by_css_selector(f'#span{week_num} table.not_empty tbody tr')
        items = [d.find_elements_by_css_selector('td.grid_event') for d in days]

        timetable = self.format_output(items, start_date)
        self.browser.quit()

        return timetable

    def format_output(self, items, start_date):
        date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
        week = []

        for day in items:
            day_json = {}
            for event in day:
                timestamp, data = self.format_event(date, event)
                day_json[timestamp] = data
            week.append(day_json)
            date = date.replace(day=date.day + 1)

        return week

    @staticmethod
    def format_event(date, event):
        def get_elem(selector):
            try:
                return event.find_element_by_css_selector(selector).text
            except NoSuchElementException:
                return ""

        def get_date(string):
            return datetime.datetime.strptime(string, '%H:%M')

        regex = r'^(\d{2}:\d{2})-(\d{2}:\d{2}) (.+)$'

        start_time, end_time, module_type = re.search(regex, get_elem('.event_title')).groups()
        timestamp = date.strftime('%d-%m-%Y') + " " + start_time
        duration = get_date(end_time) - get_date(start_time)

        event_data = {
            "nom": f"{module_type} - {get_elem('.resource_grid_module')}",
            "duration": str(duration)[:-3].replace(':', 'h'),
            "prof": get_elem('.resource_grid_staff'),
            "salle": get_elem('.resource_grid_room')
        }

        return timestamp, event_data
