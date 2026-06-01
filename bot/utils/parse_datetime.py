from dateutil import parser
from dateutil.relativedelta import relativedelta
import re
from datetime import datetime

def parse_dt(text: str) -> datetime | None:
    try:
        return parser.parse(text, fuzzy=True, default=datetime.now())
    except Exception:
        return None