import json
import os
import re
from bs4 import BeautifulSoup
import requests

DATA_FILE = "data/projects.json"
TARGET_LOCATIONS = ["praha-3", "praha-4", "praha-10", "praha-12"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def parse_project_details(container):
  text = container.get_text(" ", strip=True)

  # Extrakce developera, počtu jednotek a roku
  developer_match = re.search(r"Developer:\s*([^Počet|K|Lokalita]+)", text)
  units_match = re.search(r"Počet jednotek:\s*([^Lokalita|K|Developer]+)", text)
  year_match = re.search(r"K nastěhování od:\s*(\d{4})", text)

  return {
      "developer": (
          developer_match.group(1).strip() if developer_match else "Nespecifikováno"
      ),
      "units": units_match.group(1).strip() if units_match else "N/A",
      "move_in_year": year_match.group(1).strip() if year_match else "N/A",
  }


def fetch_and_parse():
  print("Spouštím vylepšený scraping s detaily...")
  all_projects = []
  seen_titles = set()

  # 1. Základní známé projekty v cílových lokalitách (P3, P4, P10, P12)
  curated_projects = [
      {
          "title": "Za.hraďák",
          "location": "Praha 10",
          "developer": "Sekyra Group",
          "units": "Byty & Domy",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "NOOK Strašnice",
          "location": "Praha 10",
          "developer": "ASPIRA Development",
          "units": "57",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "ELEMENT Malešice",
          "location": "Praha 10",
          "developer": "RS development",
          "units": "200+",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Vršovická 44",
          "location": "Praha 10",
          "developer": "Nespecifikováno",
          "units": "33",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Metropolis Tower",
          "location": "Praha 10",
          "developer": "Central Group",
          "units": "256",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Družstevní 5",
          "location": "Praha 4",
          "developer": "PSN",
          "units": "32",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Modřanská Zahrada",
          "location": "Praha 4",
          "developer": "IP Polná",
          "units": "151",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Rezidence Hausmannova",
          "location": "Praha 4",
          "developer": "Fetters",
          "units": "101",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "HARTIGOVA 114",
          "location": "Praha 3",
          "developer": "Nespecifikováno",
          "units": "N/A",
          "status": "V prodeji",
          "url": "https://www.novostavby.com/",
      },
  ]

  for p in curated_projects:
    seen_titles.add(p["title"])
    all_projects.append(p)

  # 2. Dynamický scraping z novostavby.com
  url = "https://www.novostavby.com/"
  try:
    res = requests.get(url, headers=HEADERS, timeout=10)
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      for a_tag in soup.find_all("a"):
        text = a_tag.get_text(strip=True)
        if any(loc in text.lower() for loc in ["praha 3", "praha 4", "praha 10", "praha 12"]):
          clean_title = text.replace(" Ceník", "").strip()
          if clean_title and clean_title not in seen_titles and len(clean_title) < 50:
            seen_titles.add(clean_title)
            loc_found = "Praha 10" if "praha 10" in text.lower() else ("Praha 4" if "praha 4" in text.lower() else "Praha 3")
            all_projects.append({
                "title": clean_title,
                "location": loc_found,
                "developer": "Novostavby.com",
                "units": "N/A",
                "status": "V prodeji",
                "url": url,
            })
  except Exception as e:
    print(f"Chyba při scrapingu: {e}")

  parsed_data = {
      "status": "success",
      "target_locations": ["Praha 3", "Praha 4", "Praha 10", "Praha 12"],
      "items_found": len(all_projects),
      "data": all_projects,
  }

  os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)

  print(f"Data úspěšně uložena ({len(all_projects)} projektů).")


if __name__ == "__main__":
  fetch_and_parse()
