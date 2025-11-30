# test_korean_portal_weather_crawler.py

from korean_portal_weather_crawler import run_crawler

def test_run_crawler_basic():
    url = "https://weather.naver.com/today/09140104"
    data = run_crawler(
        url=url,
        headless=True,
        timeout=10,
        log_level="INFO",
    )
    # minimal sanity checks
    assert data.location is not None

if __name__ == "__main__":
    test_run_crawler_basic()
