from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Global driver
driver = None

def open_website(url: str):
    global driver
    try:
        options = Options()
        options.add_argument("--no-sandbox")
        driver = webdriver.Firefox(options=options)
        driver.get(url)
    except Exception as e:
        print(f"Error opening website: {e}")
        if driver: 
            driver.quit()
        raise

def wait_for_element(by_strategy, value, timeout=10, condition=EC.presence_of_element_located):
    try:
        return WebDriverWait(driver, timeout).until(condition((by_strategy, value)))
    except Exception as e:
        print(f"Error waiting for element '{value}': {e}")
        raise

def click_enter(timeout: int = 5, wait_for_next_element_id: str = None):
    try:
        enter_button = wait_for_element(By.ID, "enterBtn", timeout, EC.element_to_be_clickable)
        enter_button.click()
        print("Clicked the Enter button")

        if wait_for_next_element_id:
            print(f"Waiting for element '{wait_for_next_element_id}' to appear after click...")
            wait_for_element(By.ID, wait_for_next_element_id, timeout, EC.visibility_of_element_located)
            print(f"Element '{wait_for_next_element_id}' is visible.")

    except Exception as e:
        print(f"Error in click_enter: {e}")

def add_db(question: str, answer: str):
    question_str = question.text if hasattr(question, 'text') else str(question)
    answer_str = answer.text if hasattr(answer, 'text') else str(answer)

    new_entry = {question_str: answer_str}
    print(f"Adding to DB: {new_entry}")
    try:
        with open("db.json", "r+") as db_file:
            data = json.load(db_file)
            data["lingos"].append(new_entry)
            db_file.seek(0) # Move pointer to start of file
            json.dump(data, db_file, indent=4)
            db_file.truncate() # Remove existing data
    except FileNotFoundError:
        with open("db.json", "w") as db_file:
            data = {"lingos": [new_entry]}
            json.dump(data, db_file, indent=4)
    except Exception as e:
        print(f"Error adding to DB: {e}")

def query_db(question: str):
    question_str = question.text if hasattr(question, 'text') else str(question)
    try:
        with open("db.json", "r") as db_file:
            data = json.load(db_file)
            # print(f"DB data: {data}") # Too verbose, uncomment for debugging
            for entry in data.get("lingos", []):
                # print(f"Checking entry: {entry}") # Too verbose, uncomment for debugging
                if question_str in entry:
                    print(f"Found translation for '{question_str}' in DB.")
                    return entry[question_str]
            print(f"Translation for '{question_str}' not found in DB.")
            return None
    except FileNotFoundError:
        print("db.json not found. Returning None.")
        return None
    except Exception as e:
        print(f"Error querying DB: {e}")
        return None

def translate_without_word():
    # Get the word to translate (the question)
    try:
        question_content_element = wait_for_element(By.ID, "flashcard_main_text", 10, EC.visibility_of_element_located)
        question_text = question_content_element.text[:100]
        print(f"To translate: {question_text}")
    except Exception as e:
        print(f"Could not get question content: {e}")
        return # Exit if we can't get the question

    translation_from_db = query_db(question_text)
    translation_to_enter = None

    if translation_from_db is None:
        # Click the Enter button to get the translation
        # Wait for 'flashcard_error_correct' (translation element) to become visible
        click_enter(5, wait_for_next_element_id="flashcard_error_correct")

        # Actually get the translation from the page
        try:
            translation_content_element = wait_for_element(By.ID, "flashcard_error_correct", 5, EC.visibility_of_element_located)
            translation_on_page = translation_content_element.text[:500]
            add_db(question_text, translation_on_page) # Use the string text for DB
            print(f"Translation from page: {translation_on_page}")
            translation_to_enter = translation_on_page
        except Exception as e:
            print(f"Could not get translation from page: {e}")
            return # Exit if we can't get the translation
        
        click_enter(5, wait_for_next_element_id="flashcard_answer_input")
    else:
        translation_to_enter = translation_from_db
        print(f"Using translation from DB: {translation_to_enter}")

    if not translation_to_enter:
        print("No translation available to enter.")
        return

    # Enter the translation into the answer box
    try:
        answer_box = wait_for_element(By.ID, "flashcard_answer_input", 10, EC.element_to_be_clickable)
        if not answer_box.is_enabled():
            print("Answer box is not enabled, attempting to enable or proceed.")
        answer_box.send_keys(translation_to_enter)
        print("Translation entered")
    except Exception as e:
        print(f"Error entering translation: {e}")
        return

    # Click Enter 2 times to get to the next question
    # First click to submit the answer
    click_enter(5, wait_for_next_element_id="flashcard_error_correct")
    click_enter(5, wait_for_next_element_id="flashcard_main_text")

def main():
    open_website("https://lingos.pl")
    print("Log in to the website and go to the learning page (e.g., 'Learn' section).")
    input("Press ENTER after the lesson is loaded: ")
    
    # Initial wait for the first question type to appear
    initial_question_type_element = wait_for_element(By.ID, "flashcard_title_text", 30, EC.visibility_of_element_located)
    print(f"Initial question type: {initial_question_type_element.text[:100]}")

    while True:
        # Get the task type
        try:
            question_type_element = wait_for_element(By.ID, "flashcard_title_text", 10, EC.visibility_of_element_located)
            question_type_text = question_type_element.text[:100]
            print(f"\nCurrent Task: {question_type_text}")
        except Exception as e:
            print(f"Error getting question type, breaking loop: {e}")
            break # Exit loop if we can't determine the question type

        if question_type_text == "Przetłumacz:":
            print("Type: translate")
            translate_without_word()
        else:
            print(f"Unknown task type: {question_type_text}. Skipping.")
            sys.exit(1)
        
    if driver:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if driver:
            driver.quit()
