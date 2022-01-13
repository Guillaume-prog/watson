import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


# Constants

SITE_URL = 'https://notes.iut-nantes.univ-nantes.fr/'
DRIVER_PATH = "/usr/bin/chromedriver"


# Functions


def get_browser():
    options = Options()
    options.add_argument("--headless")

    return Chrome(DRIVER_PATH, options=options)


def connect(b: Chrome, user, pw):
    b.get(SITE_URL)
    b.find_element_by_css_selector('input#username').send_keys(user)
    b.find_element_by_css_selector('input#password').send_keys(pw)
    b.find_element_by_css_selector('#login input.btn').click()

    time.sleep(2)


def get_marks(b: Chrome):
    m_marks = {}
    cur_ue = 0
    cur_mod = 0

    entries = b.find_elements_by_css_selector('table.notes_bulletin tbody tr')
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
                m_marks[cur_ue]["modules"][cur_mod]["notes"].append([mark,
                    e.find_element_by_css_selector("td:last-child").text[1:-1]
                ])

    return m_marks


def sort_data(m_marks):
    ue_averages = []

    total_string = ""
    sub_string = ""

    for ue_name in m_marks:
        ue = m_marks.get(ue_name)
        ue_marks = []
        for mod_name in ue.get("modules"):
            mod = ue.get("modules").get(mod_name)
            mod_average = get_average(mod.get("notes"))
            if mod_average != '/':
                sub_string += "{}: {}\n".format(mod_name, mod_average)
                ue_marks.append([mod_average, mod.get("coeff")])

        ue_average = get_average(ue_marks)
        if ue_average != '/':
            total_string += "{}: {}\n-----------\n{}\n".format(ue_name, ue_average, sub_string)
            sub_string = ""
            ue_averages.append([ue_average, ue.get("coeff")])

    total_string = "Moyenne globale: {}\n\n{}".format(get_average(ue_averages), total_string)

    return total_string.strip()


def get_average(m_list):
    m_sum = 0
    m_coeff = 0

    if len(m_list) == 0:
        return "/"

    for i in m_list:
        m_sum += float(i[0]) * float(i[1])
        m_coeff += float(i[1])
    return round(m_sum / m_coeff, 2)
