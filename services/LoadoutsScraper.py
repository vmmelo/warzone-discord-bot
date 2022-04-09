from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep


def setDriver(type='meta'):
    if type == 'meta':
        url = "https://warzoneloadout.games/"
    else:
        url = "https://warzoneloadout.games/"
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.set_window_position(0, 0)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    wait = WebDriverWait(driver, 60)
    sleep(5)
    return driver


def get_headers(driver):
    headers = []
    headersEl = driver.find_elements(By.XPATH,
                                     '/html/body/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div[1]/div/div/div/table/thead/tr/th')
    for h in headersEl:
        headers.append(h.text)
    return headers


def get_loadouts(type=''):
    driver = setDriver(type)
    headers = get_headers(driver)
    loadouts = []
    tbody = driver.find_element(By.XPATH,
                                '/html/body/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div[1]/div/div/div/table/tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    for row in range(len(rows)):
        weaponDict = {}
        for col, header in enumerate(headers):
            col_text = driver.find_element(By.XPATH,
                                           f'/html/body/div[1]/div/div/div/div/div/div/div[4]/div/div[2]/div/div[1]/div/div/div/table/tbody/tr[{row + 1}]/td[{col + 1}]').text
            if col_text != '':
                weaponDict[header] = col_text
        loadouts.append(weaponDict)
    return loadouts


def get_weapon_alias(weapon):
    aliases = {

    }
    if weapon in aliases:
        return aliases[weapon]
    return weapon


def format_loadout_to_db(loadout):
    item = {
        'weapon': loadout['Gun'],
        'alias': get_weapon_alias(loadout['Gun']),
        'content': loadout
    }
    return item

