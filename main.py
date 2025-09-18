from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


def open_website(url: str):
    global driver
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        driver = webdriver.Firefox(options=options)

        driver.get(url) # opens the link

    except Exception as e:
        print(f"Error: {e}")

        
def main():
    open_website("https://lingos.pl")

    input("Press ENTER to continue: ") # for debugging

    # Get the task type
    try:
        question_type = driver.find_element(By.ID, "flashcard_title_text")
        if question_type:
            print(question_type.text[:100])
        else:
            print("No body element found")
    except Exception as e:
        print(f"Error: {e}")

    if question_type.text[:100] == "Przetłumacz:":
        print("Type: translate")

        # Get the task content
        try:
            question_content = driver.find_element(By.ID, "flashcard_main_text")
            if question_content:
                print(f"To translate: {question_content.text[:100]}")
            else:
                print("No body element found")
        except Exception as e:
            print(f"Error: {e}")

    # TODO: Fuction to manage a translation database

    # Click the Enter button to get the translation
    timeout = 5

    try:
        enter_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "enterBtn"))
        )
        enter_button.click()
        print("Clicked the Enter button")
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2) # Wait for the website to change the url

    try:
        translation_content = driver.find_element(By.ID, "flashcard_error_correct")
        if question_content:
            print(f"Translation: {translation_content.text[:100]}")
        else:
            print("No body element found")
    except Exception as e:
        print(f"Error: {e}")


        




if __name__ == "__main__":
    main()
