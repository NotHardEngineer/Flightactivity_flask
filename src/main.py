import json

from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    g
)
from datetime import datetime
import time
from pytz import timezone
from sqlalchemy import extract
from src.utils import higher_first

from src.models import *

bp_main = Blueprint('main', __name__)


@bp_main.route("/", methods=("GET", "POST"))
def main():
    start_time = time.time()
    current_app.logger.info("Main page requested")

    if request.method == 'POST':
        day_for_seek = request.form['flights_date']
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        table_content_dep = {}
        table_content_arr = {}
        table_content_all = {}

        all_flights = s.query(Flights). \
            filter(Flights.et_date == day_for_seek). \
            with_entities(Flights.et_time, Flights.number, Flights.is_depart, Flights.company, Flights.vessel_model). \
            order_by(Flights.et_time)

        if all_flights.count() > 0:
            depart_fights = all_flights.filter(Flights.is_depart == True)
            arrive_flights = all_flights.filter(Flights.is_depart == False)
            count_by_hours_all = []
            count_by_hours_dep = []
            count_by_hours_arr = []

            for i in range(24):
                all_hour_flights = all_flights.filter(extract('hour', Flights.et_time) == i)

                table_content_dep[i] = []
                table_content_arr[i] = []
                table_content_all[i] = []

                count_by_hours_all.append(all_hour_flights.count())
                count_by_hours_dep.append(depart_fights.filter(extract('hour', Flights.et_time) == i).count())
                count_by_hours_arr.append(arrive_flights.filter(extract('hour', Flights.et_time) == i).count())

                for flight in all_hour_flights:
                    table_content_all[i].append(
                        [flight.et_time.strftime('%H:%M'), flight.number, flight.company, str(flight.is_depart),
                         flight.vessel_model])
                    if flight.is_depart == True:
                        table_content_dep[i].append(
                            [flight.et_time.strftime('%H:%M'), flight.number, flight.company, flight.vessel_model])
                    else:
                        table_content_arr[i].append(
                            [flight.et_time.strftime('%H:%M'), flight.number, flight.company, flight.vessel_model])

            data = {
                'data_all': count_by_hours_all,
                'data_dep': count_by_hours_dep,
                'data_arr': count_by_hours_arr
            }
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            current_app.logger.info("Main page returned in %s sec" % format(time.time() - start_time, '.2f'))
            return render_template("index.html",
                                   title="Самолеты в толмачево",
                                   data=data,
                                   table_content_all=table_content_all,
                                   table_content_dep=table_content_dep,
                                   table_content_arr=table_content_arr,
                                   date_for_show=date_for_show,
                                   date=day_for_seek
                                   )
        else:
            current_app.logger.info("Main page without data returned in %s sec" % format(time.time() - start_time, '.2f'))
            flash("Данные за выбранную дату не найдены, пожалуйста, попробуйте позже или выберите другую дату")
            return render_template("nodata.html")


@bp_main.route("/companies/", methods=("GET", "POST"))
def companies():
    start_time = time.time()
    current_app.logger.info("Company page requested")

    default_labels = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                      '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00',
                      '22:00', '23:00']

    if request.method == 'POST':
        day_for_seek = request.form['flights_date']
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        all_flights = s.query(Flights). \
            filter(Flights.et_date == day_for_seek). \
            with_entities(Flights.et_time, Flights.number, Flights.is_depart, Flights.company, Flights.vessel_model)

        companies_list = [i[0] for i in all_flights.with_entities(Flights.company).distinct()]
        companies_list.sort()

        all_flights = all_flights.order_by(Flights.et_time)

        all_dep = []
        all_arr = []
        all_labels = []
        all_tables_content = []

        if all_flights.count() > 0:
            for i in range(len(companies_list)):
                company = companies_list[i]
                companies_list[i] = higher_first(company)
                company_flights = all_flights.filter(Flights.company == company)
                depart_fights = company_flights.filter(Flights.is_depart == True)
                arrive_flights = company_flights.filter(Flights.is_depart == False)

                count_by_hours_dep = []
                count_by_hours_arr = []
                company_hour_labels = []
                company_table_content = {}

                for hour in range(24):

                    hour_company_flights = company_flights.filter(extract('hour', Flights.et_time) == hour)
                    hour_depart_flights = depart_fights.filter(extract('hour', Flights.et_time) == hour)
                    count_hour_depart = hour_depart_flights.count()
                    hour_arrive_flights = arrive_flights.filter(extract('hour', Flights.et_time) == hour)
                    count_hour_arrive = hour_arrive_flights.count()

                    count_by_hours_dep.append(count_hour_depart)
                    count_by_hours_arr.append(count_hour_arrive)

                    if count_hour_depart + count_hour_arrive == 1:
                        if count_hour_depart > count_hour_arrive:
                            company_hour_labels.append(str(hour_depart_flights[0].et_time)[:5])
                        else:
                            company_hour_labels.append(str(hour_arrive_flights[0].et_time)[:5])
                    else:
                        company_hour_labels.append(default_labels[hour])

                    if count_hour_depart + count_hour_arrive > 0:
                        company_table_content[hour] = []
                        for flight in hour_company_flights:
                            company_table_content[hour].append(
                                [flight.et_time.strftime('%H:%M'), flight.number, flight.is_depart,
                                 flight.vessel_model])

                all_arr.append(count_by_hours_arr)
                all_dep.append(count_by_hours_dep)
                all_labels.append(company_hour_labels)
                all_tables_content.append(company_table_content)
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            current_app.logger.info("Company page returned in %s sec" % format(time.time() - start_time, '.2f'))
            return render_template("companies.html",
                                   title="Авиакомпании в толмачево",
                                   companies=json.dumps(companies_list),
                                   labels=json.dumps(all_labels),
                                   tables_content=json.dumps(all_tables_content),
                                   all_arr=all_arr,
                                   all_dep=all_dep,
                                   date_for_show=date_for_show,
                                   date=day_for_seek)

        else:
            current_app.logger.info("Company page without data returned in %s sec" % format(time.time() - start_time, '.2f'))
            return render_template("nodata.html")
