"""
Korean Portal Weather Crawler

A small Selenium example that scrapes basic weather information
from a Korean weather portal (currently Naver Weather).

This project is for educational and portfolio purposes only and is
not affiliated with or endorsed by Naver Corporation.
"""

import argparse
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Optional

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure a basic console logger.

    This function is idempotent: if handlers are already attached,
    it will not add duplicate handlers.
    """
    logger = logging.getLogger()
    if logger.handlers:
        return

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class WeatherData:
    """
    Data model for scraped weather information.

    Attributes:
        location: Location name (e.g. city or district).
        temperature: Current temperature text.
        status: Weather description (e.g. sunny, cloudy).
    """

    location: Optional[str]
    temperature: Optional[str]
    status: Optional[str]

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Return weather data as a plain dictionary."""
        return asdict(self)

# ---------------------------------------------------------------------------
# WebDriver factory
# ---------------------------------------------------------------------------

def create_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create and configure a Chrome WebDriver instance.

    Args:
        headless: If True, run Chrome in headless mode.

    Returns:
        A configured Chrome WebDriver instance.

    Raises:
        WebDriverException: If Chrome WebDriver creation fails.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")

    # Common options for more stable scraping environments
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"]
    )

    service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver created (headless=%s)", headless)
        return driver
    except WebDriverException as e:
        logger.exception("Failed to create Chrome WebDriver: %s", e)
        raise

# ---------------------------------------------------------------------------
# Helper for safe element text extraction
# ---------------------------------------------------------------------------

def _safe_get_text(
    driver: webdriver.Chrome,
    by: By,
    selector: str,
    timeout: int = 10,
    field_name: str = "",
) -> Optional[str]:
    """
    Safely get text content from an element using WebDriverWait.

    Args:
        driver: Selenium WebDriver instance.
        by: Locator strategy (e.g. By.CSS_SELECTOR).
        selector: Locator string.
        timeout: Maximum wait time in seconds.
        field_name: Optional field name for logging.

    Returns:
        Stripped text content if found, otherwise None.
    """
    try:
        elem = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        text = elem.text.strip()
        logger.debug(
            "Element found for '%s' (%s='%s'): %r",
            field_name,
            by,
            selector,
            text,
        )
        return text or None
    except TimeoutException:
        logger.warning(
            "Timeout while waiting for element '%s' (%s='%s')",
            field_name,
            by,
            selector,
        )
        return None
    except Exception as e:
        logger.exception(
            "Unexpected error while getting text for '%s' (%s='%s'): %s",
            field_name,
            by,
            selector,
            e,
        )
        return None

# ---------------------------------------------------------------------------
# Core scraping logic
# ---------------------------------------------------------------------------

def scrape_weather(
    url: str,
    headless: bool = True,
    timeout: int = 10,
) -> WeatherData:
    """
    Scrape basic weather information from a Korean weather portal page.
    (for example, a Naver Weather URL).
    
    Args:
        url: Target weather URL (e.g. a Naver Weather page).
        headless: Whether to run the browser in headless mode.
        timeout: Maximum wait time in seconds for each element.

    Returns:
        WeatherData instance with scraped values.
    """
    logger.info("Start scraping: %s", url)
    driver = create_driver(headless=headless)

    try:
        driver.get(url)

        # NOTE:
        # These CSS selectors may change if the portal updates its layout.
        # In that case, you only need to adjust the selectors below.
        location = _safe_get_text(
            driver,
            By.CSS_SELECTOR,
            "strong.location_name, span.location_name",
            timeout=timeout,
            field_name="location",
        )
        temperature = _safe_get_text(
            driver,
            By.CSS_SELECTOR,
            ".card_data_now .card_now_temperature",
            timeout=timeout,
            field_name="temperature",
        )
        status = _safe_get_text(
            driver,
            By.CSS_SELECTOR,
            ".card_data_detail .card_date_emphasis",
            timeout=timeout,
            field_name="status",
        )

        data = WeatherData(
            location=location,
            temperature=temperature,
            status=status,
        )
        logger.info("Scraping finished: %s", data.to_dict())
        return data

    finally:
        driver.quit()
        logger.debug("WebDriver closed")

# ---------------------------------------------------------------------------
# Programmatic entry point (no argparse needed)
# ---------------------------------------------------------------------------

def run_crawler(
    url: str,
    headless: bool = True,
    timeout: int = 10,
    log_level: str = "INFO",
) -> WeatherData:
    """
    Run the crawler programmatically without relying on CLI arguments.

    This is useful for:
      - Local tests in a Python shell
      - Integration in other scripts
      - Unit tests or demo code

    Example:
        from korean_portal_weather_crawler import run_crawler

        data = run_crawler(
            url="https://weather.naver.com/today/09140104",
            headless=True,
            timeout=10,
            log_level="DEBUG",
        )
        print(data.to_dict())

    Args:
        url: Target weather URL (e.g. a Naver Weather page).
        headless: Whether to run the browser in headless mode.
        timeout: Maximum wait time in seconds for each element.
        log_level: Logging level name (e.g. 'DEBUG', 'INFO').

    Returns:
        WeatherData instance with scraped values.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    configure_logging(level=level)

    return scrape_weather(
        url=url,
        headless=headless,
        timeout=timeout,
    )

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simple Korean portal weather crawler using Selenium"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Target weather URL (e.g. a Naver Weather page)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser with UI (headless mode off)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Max wait time (seconds) for each element (default: 10)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    level = getattr(logging, args.log_level.upper(), logging.INFO)
    configure_logging(level=level)

    headless = not args.no_headless

    data = scrape_weather(
        url=args.url,
        headless=headless,
        timeout=args.timeout,
    )

    # Simple JSON-like output for CLI usage
    print(data.to_dict())


if __name__ == "__main__":
    main()

