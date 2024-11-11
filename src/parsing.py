from bs4 import BeautifulSoup
import time
import datetime as dt

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import chromedriver_binary  # We need this, don`t delete

import os
from pathlib import Path
from flask import (
    Blueprint,
    url_for,
    redirect,
    current_app
)

from src.models import session_db, Flights, Companies
from src.utils import delete_spaces

BASE_DIR = Path(__file__).resolve().parent.parent
bp_parsing = Blueprint("parsing", __name__, url_prefix='/parsing/')


@bp_parsing.route("/")
def update_all():
    start_time = time.time()
    current_app.logger.info("Full update requested")

    save_airportbaikal_tables()
    parse_saved_airport_baikal_html()
    parse_saved_airport_baikal_html(name="baikal_page_tomorrow")

    save_tolmachevo_tables()
    parse_saved_tolmachevo_html()
    parse_saved_tolmachevo_html(name="tolmachevo_page_tomorrow")

    current_app.logger.info("Update finished in %s sec" % format(time.time() - start_time, '.2f'))

    return redirect(url_for('main.main'))


def write_in_db(fn_umber: str, sh_time: str, sh_date: str, eta_time: str, eta_date: str,
                airport_iata: str, is_dep: bool, vessel: str, company: str):

    old_fid = fn_umber + str(sh_date.split(".", 1)[1]) + str(sh_date.split(".", 1)[0])

    sh_date = dt.date(dt.date.today().year, month=int(sh_date.split(".", 1)[1]), day=int(sh_date.split(".", 1)[0]))
    sh_time = dt.time(int(sh_time.split(":", 1)[0]), int(sh_time.split(":", 1)[1]))

    eta_date = dt.date(dt.date.today().year, month=int(eta_date.split(".", 1)[1]), day=int(eta_date.split(".", 1)[0]))
    eta_time = dt.time(int(eta_time.split(":", 1)[0]), int(eta_time.split(":", 1)[1]))

    new_fid = fn_umber.replace(" ", "-") + "_" + str(sh_date)

    with session_db() as s:
        exist_company = s.query(Companies).filter(Companies.name == company).first()
        if not exist_company:
            s.add(Companies(name=company))

        exist_flight = s.query(Flights).filter(Flights.fid == old_fid).first()
        if exist_flight:
            exist_flight.fid = new_fid
            exist_flight.et_time = eta_time
            exist_flight.et_date = eta_date
            exist_flight.vessel_model = vessel
            s.add(exist_flight)
        else:
            exist_flight = s.query(Flights).filter(Flights.fid == new_fid).first()
            if exist_flight:
                exist_flight.et_time = eta_time
                exist_flight.et_date = eta_date
                exist_flight.vessel_model = vessel
                s.add(exist_flight)
            else:
                f = Flights(
                    fid=new_fid,
                    number=fn_umber,
                    sh_time=sh_time,
                    sh_date=sh_date,
                    et_time=eta_time,
                    et_date=eta_date,
                    airport_iata=airport_iata,
                    is_depart=is_dep,
                    vessel_type='plane',
                    vessel_model=vessel,
                    company=company)
                s.add(f)

        s.commit()


@bp_parsing.route("/updatefids")
def update_fids():
    start_time = time.time()
    current_app.logger.info("FID update started")

    with session_db() as s:
        flights = s.query(Flights)
        for flight in flights:
            new_fid = flight.number.replace(" ", "-") + "_" + str(flight.sh_date)
            flight.fid = new_fid
            s.add(flight)
        s.commit()

    current_app.logger.info("Updating FIDs finished in %s sec" % format(time.time() - start_time, '.2f'))
    return redirect(url_for('main.main'))



def save_tolmachevo_tables(destination=os.path.join(BASE_DIR, "saved_pages"), name='tolmachevo_page'):
    start_time = time.time()
    current_app.logger.info("Saving tolmachevo tables started")

    if not os.path.exists(destination):
        os.makedirs(destination)
    url_to_save = 'https://tolmachevo.ru/passengers/information/timetable'

    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_to_save)
        element = WebDriverWait(driver, timeout=100, poll_frequency=1) \
            .until(lambda d: d.find_element(By.XPATH,
                                            "/html/body/div[3]/div[3]/section/div/div/section/header/div[2]/span[3]"))
        with open(destination + "/" + name + ".html", "w", encoding='utf-8') as f:
            f.write(driver.page_source)
        element.click()

        time.sleep(1)  # ПЕРЕДЕЛАТЬ ПОЗЖЕ НА АСИНХРОНКУ

        with open(destination + "/" + name + "_tomorrow.html", "w", encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()

        current_app.logger.info("Saving tolmachevo tables finished in %s sec" % format(time.time() - start_time, '.2f'))
    except selenium.common.exceptions.WebDriverException as e:
        current_app.logger.error("Saving tolmachevo tables failed in %s sec" % format(time.time() - start_time, '.2f'), exc_info=e)


def save_airportbaikal_tables(destination=os.path.join(BASE_DIR, "saved_pages"), name='baikal_page'):
    start_time = time.time()
    current_app.logger.info("Saving airportbaikal tables started")

    if not os.path.exists(destination):
        os.makedirs(destination)
    url_to_save = 'https://airportbaikal.ru/passengers/information/timetable'

    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_to_save)
        element = WebDriverWait(driver, timeout=20, poll_frequency=1) \
            .until(lambda d: d.find_element(By.XPATH,
                                            "/html/body/div[2]/div[4]/section/div/div/section/header/div[2]/span[3]"))
        with open(destination + "/" + name + ".html", "w", encoding='utf-8') as f:
            f.write(driver.page_source)
        element.click()

        time.sleep(1)  # ПЕРЕДЕЛАТЬ ПОЗЖЕ НА АСИНХРОНКУ

        with open(destination + "/" + name + "_tomorrow.html", "w", encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.quit()

        current_app.logger.info("Saving baikal tables finished in %s sec" % format(time.time() - start_time, '.2f'))
    except selenium.common.exceptions.WebDriverException as e:
        current_app.logger.error("Saving baikal tables failed in %s sec" % format(time.time() - start_time, '.2f'), exc_info=e)



def parse_saved_tolmachevo_html(destination=os.path.join(BASE_DIR, "saved_pages"), name='tolmachevo_page'):
    items = 0
    start_time = time.time()
    current_app.logger.info("Parsing tolmachevo tables started")

    target = destination + "/" + name + ".html"
    html_file = open(target, "r")
    index = html_file.read()
    parse = BeautifulSoup(index, 'lxml')

    for flight in parse.find_all('article', class_='flight-item'):
        is_dep = False
        number, s_time, s_date, e_time, e_date, vessel_type, company = ['' for _ in range(7)]
        flightdata = [i.text.lower() for i in list(flight.find_all("li"))]
        for item in flightdata:
            item_title, item_data = item.split(":", 1)
            if "расчетное время" in item_title:
                e_time, e_date = item_data.split(",", 1)
                e_time = delete_spaces(e_time)
                e_date = delete_spaces(e_date)
            elif "посадка" in item_title:
                is_dep = True
            elif "тип вс" in item_title:
                vessel_type = delete_spaces(item_data)
            elif "по расписанию" in item_title:
                s_time, s_date = item_data.split(",", 1)
                s_time = delete_spaces(s_time)
                s_date = delete_spaces(s_date)
            elif "номер рейса" in item_title:
                number = delete_spaces(item_data)
            elif "компания" in item_title:
                company = delete_spaces(item_data)
        write_in_db(fn_umber=number, sh_time=s_time, sh_date=s_date, eta_time=e_time, eta_date=e_date,
                    airport_iata='obv', is_dep=is_dep, vessel=vessel_type, company=company)
        items += 1

    current_app.logger.info("Parsing tolmachevo tables finished in %s sec, %i items parsed" % (format(time.time() - start_time, '.2f'), items))


def parse_saved_airport_baikal_html(destination=os.path.join(BASE_DIR, "saved_pages"), name='baikal_page'):
    items = 0
    start_time = time.time()
    current_app.logger.info("Parsing airport_baikal tables started")

    target = destination + "/" + name + ".html"
    html_file = open(target, "r")
    index = html_file.read()
    parse = BeautifulSoup(index, 'lxml')

    for flight in parse.find_all('article', class_='flight-item'):
        is_dep = False
        number, s_time, s_date, e_time, e_date, vessel_type, company = ['' for _ in range(7)]
        flightdata = [i.text.lower() for i in list(flight.find_all("li"))]
        for item in flightdata:
            item_title, item_data = item.split(":", 1)
            if "расчетное время" in item_title:
                e_time, e_date = item_data.split(",", 1)
                e_time = delete_spaces(e_time)
                e_date = delete_spaces(e_date)
            elif "посадка" in item_title:
                is_dep = True
            elif "тип вс" in item_title:
                vessel_type = delete_spaces(item_data)
            elif "по расписанию" in item_title:
                s_time, s_date = item_data.split(",", 1)
                s_time = delete_spaces(s_time)
                s_date = delete_spaces(s_date)
            elif "номер рейса" in item_title:
                number = delete_spaces(item_data)
            elif "компания" in item_title:
                company = delete_spaces(item_data)
        write_in_db(fn_umber=number, sh_time=s_time, sh_date=s_date, eta_time=e_time, eta_date=e_date,
                    airport_iata='uud', is_dep=is_dep, vessel=vessel_type, company=company)
        items += 1

    current_app.logger.info("Parsing airport_baikal tables finished in %s sec, %i items parsed" % (format(time.time() - start_time, '.2f'), items))
