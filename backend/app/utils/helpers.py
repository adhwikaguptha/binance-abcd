import json
from datetime import datetime
from decimal import Decimal

def safe_json_dumps(data):
    """Safely serialize objects (like Decimal, datetime) to JSON."""
    def default(o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    return json.dumps(data, default=default)
