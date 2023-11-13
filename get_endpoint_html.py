import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # type: ignore
from selenium.common.exceptions import TimeoutException


# Author: Ayush Garg


def setup_driver():
    """
    The function `setup_driver` returns a Chrome WebDriver instance with specified options and settings.
    :return: The function `setup_driver()` returns a Chrome WebDriver instance.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    )
    options.add_experimental_option(
        "prefs",
        {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        },
    )

    chrome_driver_path = "/usr/bin/chromedriver"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def safe_click_element(driver, element):
    """
    The `safe_click_element` function is a Python code snippet that attempts to click on a web element
    in a safe manner, handling potential exceptions and using different strategies if necessary.

    :param driver: The "driver" parameter is an instance of a WebDriver, which is used to interact with
    a web browser. It allows you to navigate to web pages, interact with elements on the page, and
    perform various actions
    :param element: The `element` parameter is the web element that you want to click on. It can be any
    valid web element object, such as an instance of `WebElement` class in Selenium
    """
    try:
        # Wait for the element to be clickable
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, element.get_attribute("outerHTML")))
        )
        element.click()
    except ElementClickInterceptedException:
        # If the element is not clickable, scroll to it and try again
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()
    except:
        # If it still doesn't work, use JavaScript to click on the element
        driver.execute_script("arguments[0].click();", element)


def connect_to_url(driver, url):
    try:
        driver.get(url)
        return True
    except Exception as e:
        print(f"Error connecting to URL: {e}")
        return False


def wait_for_page_load(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return True
    except TimeoutException:
        print("Timeout while waiting for page to load.")
        return False
    except Exception as e:
        print(f"Error waiting for page load: {e}")
        return False


def extract_page_elements(driver):
    try:
        title = driver.title
        body_text = driver.find_element(By.TAG_NAME, "body").text
        headers = [header.text for header in driver.find_elements(By.TAG_NAME, "h1")]
        navigation_menu = driver.find_element(By.TAG_NAME, "nav")
        footer = driver.find_element(By.TAG_NAME, "footer")
        images = driver.find_elements(By.TAG_NAME, "img")

        return {
            "title": title,
            "body_text": body_text,
            "headers": headers,
            "navigation_items": navigation_menu.text.split("\n")
            if navigation_menu
            else [],
            "footer_content": footer.text if footer else "",
            "image_count": len(images),
        }
    except Exception as e:
        print(f"Error extracting page elements: {e}")
        return None


def get_page_text(driver, url):
    if not connect_to_url(driver, url):
        return None

    if not wait_for_page_load(driver):
        return None

    website_summary = extract_page_elements(driver)
    if website_summary is None:
        return "I couldn't retrieve the text of the website, just enter a compliment for a website"

    return str(website_summary)[:3700]


def click_expand_buttons(driver):
    """
    The function `click_expand_buttons` clicks on "Expand section" buttons and "Read more" paragraphs on
    a webpage using Selenium.

    :param driver: The "driver" parameter is an instance of a web driver, such as Selenium's WebDriver,
    that is used to interact with a web page. It is responsible for finding elements on the page and
    performing actions like clicking on buttons or links
    """
    # Clicking "Expand section" buttons
    expand_buttons = driver.find_elements(
        By.XPATH,
        '//button[contains(@class, "chapter-expand") and contains(text(), "Expand section")]',
    )
    for button in expand_buttons:
        safe_click_element(driver, button)
        time.sleep(1)  # Wait for the section to expand

    # Clicking "Read more" paragraphs
    read_more_elements = driver.find_elements(
        By.XPATH,
        '//p[contains(@class, "expand-paras") and contains(text(), "Read more...")]',
    )
    for element in read_more_elements:
        safe_click_element(driver, element)
        time.sleep(1)  # Wait for the section to expand


def extract_text_from_elements(driver, tag_name):
    """
    The function extracts text from elements with a specified tag name using a Selenium WebDriver.

    :param driver: The "driver" parameter is an instance of a web driver, such as Selenium WebDriver,
    that is used to interact with a web page. It is responsible for navigating to the page, finding
    elements, and performing actions on them
    :param tag_name: The tag name is a string that represents the HTML tag name of the elements you want
    to extract text from. For example, if you want to extract text from all the <p> tags on a webpage,
    you would pass "p" as the tag_name parameter
    :return: a list of text extracted from elements found by the given tag name.
    """
    elements = driver.find_elements(By.TAG_NAME, tag_name)
    return [element.text.strip() for element in elements if element.text.strip()]


def save_to_file(filename, content):
    """
    The function `save_to_file` saves the given content to a file with the specified filename.

    :param filename: The filename parameter is a string that represents the name of the file you want to
    save the content to
    :param content: The content parameter is the data that you want to save to the file. It can be a
    string, a list of strings, or any other data type that can be converted to a string
    """
    with open(filename, "w") as f:
        f.write(content)
