"""
Получить из таблицы ConsultationRequest (view To_remind) записи
где
статус new,
пустое поле reminder,
назначен консультант
и прошло 24 часа после создания записи

Обновить эти записи в таблице с установкой поля reminder в текущие дата и время
"""

import os
from dotenv import load_dotenv
from pyairtable import Api
from pyairtable.formulas import GTE, DATETIME_DIFF, NOW, Field

load_dotenv()

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID = os.environ["DATABASE_ID"]
TABLE_REQUEST_ID = os.environ["TABLE_REQUEST_ID"]  # ConsultationRequest

api = Api(AIRTABLE_API_KEY)

table = api.table(BASE_ID, TABLE_REQUEST_ID)

formula = GTE(DATETIME_DIFF(NOW(), Field("created_at"), "hours"), 24)
new_requests = table.all(view="To_remind", formula=formula)

for request in new_requests:
    table.update(request["id"], {"reminder": NOW()})

print("Done")

exit(0)
