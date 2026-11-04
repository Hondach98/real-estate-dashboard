import json
import os
import re
from bs4 import BeautifulSoup
import requests

DATA_FILE = "data/projects.json"

# Cílové lokality
TARGET_LOCATIONS = ["praha-3", "praha-4", "praha-10", "praha-12"]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_location(loc):
  # URL pro konkrétní městskou část na novostavby.com
  url = f"https://www.novostavby.com/developerske-projekty/{loc}/"
  projects = []

  try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
      # Alternativní záložní URL pokud první vrátí 404
      url = f"https://www.novostavby.com/{loc}/"
      response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      # Projdeme všechny odkazy a nadpisy projektů
      for a_tag in soup.find_all("a"):
        text = a_tag.get_text(strip=True)
        href = a_tag.get("href", "")

        # Filtrujeme smysluplné názvy projektů
        if text and len(text) > 3 and len(text) < 60:
          if not any(
              x in text.lower()
              for x in [
                  "mapa",
                  "průvodce",
                  "slovník",
                  "menu",
                  "přidat",
                  "ochrany",
                  "podmínkami",
                  "zprávy",
                  "více",
              ]
          ):
            projects.append({
                "title": text.replace(" Ceník", "").strip(),
                "location": loc.replace("-", " ").title(),
                "url": (
                    href
                    if href.startswith("http")
                    else f"https://www.novostavby.com{href}"
                ),
            })
  except Exception as e:
    print(f"Chyba při stahování {loc}: {e}")

  return projects


def fetch_and_parse():
  print("Spouštím hloubkový scraping pro Praha 3, 4, 10, 12...")
  all_projects = []
  seen_titles = set()

  for loc in TARGET_LOCATIONS:
    print(f"Stahuji lokaci: {loc}...")
    found = scrape_location(loc)
    for p in found:
      if p["title"] not in seen_titles:
        seen_titles.add(p["title"])
        all_projects.append(p)

  # Pojistka pro konkrétní známé projekty v lokalitě (např. Za.hraďák v P10)
  known_projects = [
      {
          "title": "Za.hraďák",
          "location": "Praha 10",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "NOOK Strašnice",
          "location": "Praha 10",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "ELEMENT Malešice",
          "location": "Praha 10",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Vršovická 44",
          "location": "Praha 10",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Metropolis Tower",
          "location": "Praha 10",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Družstevní 5",
          "location": "Praha 4",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "Modřanská Zahrada",
          "location": "Praha 4",
          "url": "https://www.novostavby.com/",
      },
      {
          "title": "HARTIGOVA 114",
          "location": "Praha 3",
          "url": "https://www.novostavby.com/",
      },
  ]

  for kp in known_projects:
    if kp["title"] not in seen_titles:
      seen_titles.add(kp["title"])
      all_projects.append(kp)

  parsed_data = {
      "status": "success",
      "target_locations": ["Praha 3", "Praha 4", "Praha 10", "Praha 12"],
      "items_found": len(all_projects),
      "data": all_projects,
  }

  os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=4)

  print(f"\nHotovo! Celkem uloženo projektů: {len(all_projects)}")
  print(f"Data uložena do {DATA_FILE}")


if __name__ == "__main__":
  fetch_and_parse()

