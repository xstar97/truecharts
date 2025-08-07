import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid


def fetch_balfolk_events():
    url = "https://www.balfolk.nl/agenda/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    for li in soup.select("ul#response li.flex-container"):
        date_location = li.select_one(".date")
        title = li.select_one(".title a")

        if not date_location or not title:
            continue

        date_loc_text = date_location.text.strip()
        title_text = title.text.strip()

        try:
            # "di 12 aug 2025 | Gent" → "12 aug 2025"
            date_part, location = map(str.strip, date_loc_text.split("|"))
            date_clean = " ".join(date_part.split(" ")[1:])
            event_date = datetime.strptime(date_clean, "%d %b %Y")
        except Exception as e:
            print(f"Skipping: {e} → {date_loc_text}")
            continue

        events.append({
            "date": event_date,
            "name": title_text,
            "location": location
        })

    return events


def generate_ical(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Balfolk Calendar//EN"
    ]

    for e in events:
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{e['date'].strftime('%Y%m%d')}",
            f"SUMMARY:{e['name']}",
            f"LOCATION:{e['location']}",
            "END:VEVENT"
        ]

    lines.append("END:VCALENDAR")
    return "\n".join(lines)


if __name__ == "__main__":
    events = fetch_balfolk_events()
    ical = generate_ical(events)

    with open("balfolk.ics", "w", encoding="utf-8") as f:
        f.write(ical)

    print("✅ Saved calendar as 'balfolk.ics'")
