from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time


def open_website(url: str):
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        driver = webdriver.Firefox(options=options)

        driver.get(url) # opens the link

        time.sleep(5) # temporary browser open time

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if 'driver' in locals() and driver: # Checks if the driver is present
            driver.quit()

def main():
    pass

if __name__ == "__main__":
    open_website("https://google.com")
