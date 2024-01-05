import json

from flask import (
    Blueprint,
    render_template,
    request,
)
from datetime import datetime
from pytz import timezone
from sqlalchemy import extract
from src.utils import higher_first

from src.models import *

bp_main = Blueprint('main', __name__)


@bp_main.route("/", methods=("GET", "POST"))
def main():
    if request.method == 'POST':
        day_for_seek = request.form['flights_date']
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        table_content_dep = []
        all_flights = s.query(Flights).filter(Flights.et_date == day_for_seek)
        if all_flights.count() > 0:
            depart_fights = all_flights.filter(Flights.is_depart == True)
            arrive_flights = all_flights.filter(Flights.is_depart == False)
            count_by_hours_all = []
            count_by_hours_dep = []
            count_by_hours_arr = []

            for i in range(24):
                count_by_hours_all.append(all_flights.filter(extract('hour', Flights.et_time) == i).count())

                count_by_hours_dep.append(depart_fights.filter(extract('hour', Flights.et_time) == i).count())

                count_by_hours_arr.append(arrive_flights.filter(extract('hour', Flights.et_time) == i).count())

            for flight in depart_fights:
                table_content_dep.append([flight.number, flight.et_time.strftime('%H:%M'), flight.company])

            data = {
                'data_all': count_by_hours_all,
                'data_dep': count_by_hours_dep,
                'data_arr': count_by_hours_arr
            }
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            return render_template("index.html",
                                   title="Самолеты в толмачево",
                                   data=data,
                                   table_content_dep=table_content_dep,
                                   date_for_show=date_for_show,
                                   date=day_for_seek,
                                   )
        else:
            return render_template("nodata.html")


@bp_main.route("/companies/", methods=("GET", "POST"))
def companies():
    default_labels = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']

    if request.method == 'POST':
        day_for_seek = request.form['flights_date']
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        all_flights = s.query(Flights).filter(Flights.et_date == day_for_seek)
        companies_list = [i[0] for i in all_flights.with_entities(Flights.company).distinct()]
        companies_list.sort()
        all_dep = []
        all_arr = []
        all_labels = []

        if all_flights.count() > 0:
            for i in range(len(companies_list)):
                company = companies_list[i]
                companies_list[i] = higher_first(company)
                company_flights = all_flights.filter(Flights.company == company)
                depart_fights = company_flights.filter(Flights.is_depart == True)
                arrive_flights = company_flights.filter(Flights.is_depart == False)

                count_by_hours_dep = []
                count_by_hours_arr = []
                hour_labels = []

                for hour in range(24):
                    hour_depart_flights = depart_fights.filter(extract('hour', Flights.et_time) == hour)
                    count_hour_depart = hour_depart_flights.count()
                    hour_arrive_flights = arrive_flights.filter(extract('hour', Flights.et_time) == hour)
                    count_hour_arrive = hour_arrive_flights.count()

                    count_by_hours_dep.append(count_hour_depart)
                    count_by_hours_arr.append(count_hour_arrive)

                    if count_hour_depart + count_hour_arrive == 1:
                        if count_hour_depart > count_hour_arrive:
                            hour_labels.append(str(hour_depart_flights[0].et_time)[:5])
                        else:
                            hour_labels.append(str(hour_arrive_flights[0].et_time)[:5])
                    else:
                        hour_labels.append(default_labels[hour])

                all_arr.append(count_by_hours_arr)
                all_dep.append(count_by_hours_dep)
                all_labels.append(hour_labels)
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            return render_template("companies.html",
                                   title="Авиакомпании в толмачево",
                                   companies=json.dumps(companies_list),
                                   labels=json.dumps(all_labels),
                                   all_arr=all_arr,
                                   all_dep=all_dep,
                                   date_for_show=date_for_show,
                                   date=day_for_seek)

        else:
            return render_template("nodata.html")
