# Korean Portal Weather Crawler

A small, production-style example of using **Selenium** and **webdriver-manager**  
to scrape basic weather information from a Korean weather portal  
(demonstrated with [Naver Weather](https://weather.naver.com)).

> This project is **unofficial** and not affiliated with or endorsed by Naver.
> It is intended for learning and portfolio purposes only.

This project is designed as a clean portfolio piece:
- Type hints and dataclasses
- Structured logging
- WebDriverWait for robust element lookup
- Both CLI and programmatic usage

---

## Features

- Scrapes:
  - Location name
  - Current temperature (text)
  - Weather status (e.g. sunny, cloudy)
- Uses `WebDriverWait` instead of hard-coded `sleep`
- Works in both headless and non-headless mode
- Can be used:
  - From the command line
  - Directly from Python code (`run_crawler` function)

---

## Requirements

- Python 3.9+
- Google Chrome installed
- The following Python packages:
  - `selenium`
  - `webdriver-manager`

See [`requirements.txt`](./requirements.txt) for the exact list.

---

## Installation

```bash
git clone https://github.com/sydsyd0310/korean_portal_weather_crawler.git
cd korean_portal_weather_crawler

python -m venv venv
source venv/bin/activate    # on Windows (PowerShell): .\venv\Scripts\Activate.ps1
                            # on Windows (cmd): venv\Scripts\activate
pip install -r requirements.txt