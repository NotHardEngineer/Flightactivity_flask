from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
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
            data = {
                'data_all': count_by_hours_all,
                'data_dep': count_by_hours_dep,
                'data_arr': count_by_hours_arr
            }
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            return render_template("index.html", data=data, date_for_show=date_for_show,
                                   date=day_for_seek)
        else:
            return render_template("nodata.html")


@bp_main.route("/companies", methods=("GET", "POST"))
def companies():
    if request.method == 'POST':
        day_for_seek = request.form['flights_date']
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
        print(type(day_for_seek), day_for_seek)
    with session_db() as s:
        all_flights = s.query(Flights).filter(Flights.et_date == day_for_seek)
        companies_list = [i[0] for i in all_flights.with_entities(Flights.company).distinct()]
        companies_list.sort()
        flights_data = {}
        if all_flights.count() > 0:
            for company in companies_list:
                company_flights = all_flights.filter(Flights.company == company)
                depart_fights = company_flights.filter(Flights.is_depart == True)
                arrive_flights = company_flights.filter(Flights.is_depart == False)
                count_by_hours_dep = []
                count_by_hours_arr = []
                for i in range(24):
                    count_by_hours_dep.append(depart_fights.filter(extract('hour', Flights.et_time) == i).count())
                    count_by_hours_arr.append(arrive_flights.filter(extract('hour', Flights.et_time) == i).count())
                flights_data[
                    f'{higher_first(company)}, кол-во рейсов: {sum(count_by_hours_dep) + sum(count_by_hours_arr)}'] = {
                    'flights_arr': count_by_hours_arr,
                    'flights_dep': count_by_hours_dep}
            date_for_show = datetime.strptime(day_for_seek, '%Y-%m-%d').strftime('%d.%m.%Y')
            return render_template("companies.html", data=flights_data, date_for_show=date_for_show,
                                   date=day_for_seek)

        else:
            return render_template("nodata.html")
