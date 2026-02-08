"""
Получить данные из таблиц базы данных (Airtable)
Сформировать отчёт
Записать отчёт в файл css
Выслать отчёт по почте
"""

import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pyairtable import Api
from pyairtable.formulas import LTE, DATETIME_DIFF, TODAY, Field
from statistics import mean

load_dotenv()

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID = os.environ["DATABASE_ID"]
TABLE_REQUEST_ID = os.environ["TABLE_REQUEST_ID"]  # ConsultationRequest
TABLE_CONSULTANT_ID = os.environ["TABLE_CONSULTANT_ID"]  # Consultant

api = Api(AIRTABLE_API_KEY)

table = api.table(BASE_ID, TABLE_REQUEST_ID)

formula = LTE(DATETIME_DIFF(TODAY(), Field("created_at"), "days"), 7)
new_requests = table.all(formula=formula)

new_requests_count = len(new_requests)

formula = LTE(DATETIME_DIFF(TODAY(), Field("closed"), "days"), 7)
closed_requests = table.all(formula=formula)

closed_requests_count = len(closed_requests)

durations = [x["fields"]["duration"] for x in closed_requests]
average_duration = mean(durations)


table = api.table(BASE_ID, TABLE_CONSULTANT_ID)
consultants = table.all(
    max_records=3,
    view="By_count_of_completed_requests",
    fields=["name", "email", "number-completed-requests"],
)

best_consultants = [
    {
        "name": x["fields"]["name"],
        "email": x["fields"]["email"],
        "count": x["fields"]["number-completed-requests"],
    }
    for x in consultants
]

# создать текст отчёта

yesterday = datetime.now() - timedelta(days=1)
first_day = datetime.now() - timedelta(days=7)

html_report = f"""
<div style="background-color: darkseagreen; padding: 15px; margin: 0px">
  <h3>Week report {first_day.strftime("%Y-%m-%d")} - {yesterday.strftime("%Y-%m-%d")}</h3>
  <ul>
    <li>Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
    <li>Number of new requests: {new_requests_count}</li>
    <li>Number of completed requests: {closed_requests_count}</li>
    <li>Average duration: {average_duration:.1f} hours</li>
  </ul>

  <h4>Top 3 consultants</h4>
  <table>
"""
for consultant in best_consultants:
    html_report += f"""
    <tr>
      <td>{consultant["name"]}</td>
      <td>{consultant["email"]}</td>
      <td>{consultant["count"]}</td>
    </tr>"""
html_report += "  </table></div>"

print(html_report)


# save report into csv file
data = [
    ["Week report", first_day.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")],
    ["Created:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    ["Number of new requests:", new_requests_count],
    ["Number of completed requests:", closed_requests_count],
    ["Average duration:", f"{average_duration:.1f} hours"],
    [""],
    ["Top 3 consultants"],
]
for consultant in best_consultants:
    data.append([consultant["name"], consultant["email"], consultant["count"]])

file_name = f"/data/files/week-report-{datetime.now().strftime('%Y-%m-%d')}.csv"
with open(file_name, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(data)

exit(0)
