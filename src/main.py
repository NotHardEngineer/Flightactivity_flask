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
import json

from src.models import *

bp_main = Blueprint('main', __name__)


@bp_main.route("/", methods=("GET", "POST"))
def main():
    if request.method == 'POST':
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        all_flights = s.query(Flights).filter(Flights.et_date == day_for_seek)
        if all_flights.count() > 0:
            depart_fights = all_flights.filter(Flights.is_depart==True)
            arrive_flights = all_flights.filter(Flights.is_depart==False)
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
            return render_template("index.html", data=data)
        else:
            return render_template("nodata.html")


@bp_main.route("/companies", methods=("GET", "POST"))
def companies():
    if request.method == 'POST':
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    else:
        day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        all_flights = s.query(Flights).filter(Flights.et_date == day_for_seek)
        companies_list = [i[0] for i in all_flights.with_entities(Flights.company).distinct()]
        print(type(companies_list))
        data_for_graph_dep = []
        data_for_graph_arr = []
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
                data_for_graph_dep.append(count_by_hours_dep)
                data_for_graph_arr.append(count_by_hours_arr)

            companies_list = json.dumps(companies_list)
            data = {
                'providedDataDep': data_for_graph_dep,
                'providedDataArr': data_for_graph_arr,
                'companyList': companies_list
            }
            print(data)
            return render_template("companies.html", data=data)

        else:
            return render_template("nodata.html")


@bp_main.route("/test")
def test_write():
    day_for_seek = datetime.today().astimezone(tz=timezone("Asia/Novosibirsk")).date().strftime('%Y-%m-%d')
    with session_db() as s:
        flight = s.query(Flights).filter(Flights.et_date == day_for_seek).first()
        print(flight.et_time, type(flight.et_time))
    return redirect(url_for("hello"))
