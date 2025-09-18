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


def click_enter(timeout: int=5):
    try:
        enter_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "enterBtn"))
        )
        enter_button.click()
        print("Clicked the Enter button")
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2) # Wait for the website to change the url

        
def main():
    open_website("https://lingos.pl")

    input("Press ENTER to continue: ") # for debugging

    while True:
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
        click_enter(5)

        # Actually get the translation
        try:
            translation_content = driver.find_element(By.ID, "flashcard_error_correct")
            if question_content:
                translation = translation_content.text[:500]
                print(f"Translation: {translation_content.text[:500]}")
            else:
                print("No body element found")
        except Exception as e:
            print(f"Error: {e}")

        # Get back to the task
        click_enter(5)

        # Enter the translation into the answer box, no seperate function
        timeout = 5
        try:
            answer_box = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, "flashcard_answer_input"))
            )
            if not answer_box.is_enabled():
                print("Answer box is not enabled")

            answer_box.send_keys(translation)
            print("Translation entered")

        except Exception as e:
            print(f"Error: {e}")

        # Click Enter 2 times to get to the next question
        click_enter(5)
        time.sleep(2)
        click_enter(5)


if __name__ == "__main__":
    main()
