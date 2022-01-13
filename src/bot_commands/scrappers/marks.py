import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


class MarksClient:
    SITE_URL = 'https://notes.iut-nantes.univ-nantes.fr/'

    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.busy = False

    def wait_until_available(self):
        while self.busy:
            time.sleep(1)

    def __get_new_browser(self):
        options = Options()
        options.add_argument('--headless')

        return Chrome(self.driver_path, options=options)

    def __connect(self, browser, user, pw):
        browser.get(self.SITE_URL)
        browser.find_element_by_css_selector('input#username').send_keys(user)
        browser.find_element_by_css_selector('input#password').send_keys(pw)
        browser.find_element_by_css_selector('#login input.btn').click()

        time.sleep(2)

    def get_marks(self, user, pw):
        m_marks = {}
        cur_ue = 0
        cur_mod = 0

        self.busy = True
        browser = self.__get_new_browser()

        self.__connect(browser, user, pw)

        entries = browser.find_elements_by_css_selector('table.notes_bulletin tbody tr')
        for e in entries:
            e_type = e.get_attribute("class").split("_")[-1]

            if e_type == "ue":
                cur_ue = e.find_element_by_css_selector("td:first-child").text
                m_marks[cur_ue] = {
                    "coeff": e.find_element_by_css_selector("td:last-child").text,
                    "modules": {}
                }
            elif e_type == "mod":
                cur_mod = e.find_element_by_css_selector("td:nth-child(3)").text
                m_marks[cur_ue]["modules"][cur_mod] = {
                    "coeff": e.find_element_by_css_selector("td:last-child").text,
                    "notes": []
                }
            else:
                mark = e.find_element_by_css_selector("td.note").text
                if mark == 'ABS':
                    mark = "0"

                if mark != 'EXC' and mark != 'NP':
                    m_marks[cur_ue]["modules"][cur_mod]["notes"]\
                        .append([mark, e.find_element_by_css_selector("td:last-child").text[1:-1]])

        browser.quit()
        self.busy = False
        return m_marks

    def sort_data(self, m_marks):
        ue_averages = []

        total_string = ""
        sub_string = ""

        for ue_name in m_marks:
            ue = m_marks.get(ue_name)
            ue_marks = []
            for mod_name in ue.get("modules"):
                mod = ue.get("modules").get(mod_name)
                mod_average = self.get_average(mod.get("notes"))
                if mod_average != '/':
                    sub_string += "{}: {}\n".format(mod_name, mod_average)
                    ue_marks.append([mod_average, mod.get("coeff")])

            ue_average = self.get_average(ue_marks)
            if ue_average != '/':
                total_string += "{}: {}\n-----------\n{}\n".format(ue_name, ue_average, sub_string)
                sub_string = ""
                ue_averages.append([ue_average, ue.get("coeff")])

        total_string = "Moyenne globale: {}\n\n{}".format(self.get_average(ue_averages), total_string)

        return total_string.strip()

    def stop(self):
        self.browser.close()
        self.busy = False

    @staticmethod
    def get_average(m_list):
        m_sum = 0
        m_coeff = 0

        if len(m_list) == 0:
            return "/"

        for i in m_list:
            m_sum += float(i[0]) * float(i[1])
            m_coeff += float(i[1])
        return round(m_sum / m_coeff, 2)
