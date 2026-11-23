from datetime import datetime
import math
import re

FLIGHT_ID_REGEX = re.compile(r"^[A-Za-z0-9]{2,8}$")
AIRPORT_REGEX = re.compile(r"^[A-Z]{3}$")
DATETIME_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")

def load_airports(path: str) -> set[str]:
    airports = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            airports.add(line)
    return airports

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"
    
    stripped = [f.strip() for f in fields]
    
    for f in stripped:
        if not f:
            return "MISSING_FIELD"
            
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped
    
    if not FLIGHT_ID_REGEX.match(flight_id):
        return "INVALID_FLIGHT_ID"
        
    if not AIRPORT_REGEX.match(origin) or origin not in airports:
        return "INVALID_ORIGIN"
   
    if not AIRPORT_REGEX.match(destination) or destination not in airports:
        return "INVALID_DESTINATION"
        
  
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
        
    if not DATETIME_REGEX.match(dep_str):
        return "INVALID_DEPARTURE"
    try:
        dep_dt = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_DEPARTURE"
        

    if not DATETIME_REGEX.match(arr_str):
        return "INVALID_ARRIVAL"
    try:
        arr_dt = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_ARRIVAL"
        
   
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"
        
    
    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
 
    if price <= 0:
        return "NON_POSITIVE_PRICE"
        
    return None

def to_record(fields: list[str]) -> dict:
    stripped = [f.strip() for f in fields]
    return {
        "flight_id": stripped[0],
        "origin": stripped[1],
        "destination": stripped[2],
        "departure_datetime": stripped[3],
        "arrival_datetime": stripped[4],
        "price": float(stripped[5])
    }