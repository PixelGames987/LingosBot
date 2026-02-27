from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from dotenv import load_dotenv

import time
import json
import sys
import os
import random

load_dotenv()

AUTOMATED_LOGIN = int(os.getenv("AUTOMATED_LOGIN"))
LESSON_COUNT = int(os.getenv("LESSON_COUNT"))
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
FORCE_WAIT_SEC = int(os.getenv("FORCE_WAIT_SEC"))
CHANCE_OF_PASSING = float(os.getenv("CHANCE_OF_PASSING"))
HEADLESS = int(os.getenv("HEADLESS"))
CLEAR_DB_BEFORE_SESSION = bool(os.getenv("CLEAR_DB_BEFORE_SESSION"))

driver = None


def remove_db():
    # This function is essential when running this bot in prod
    print(f"REMOVING ALL DATABASE ENTRIES...")

    try:
        with open("db.json", "r+") as db_file:
            data = json.load(db_file)
            data["lingos"] = []
            db_file.seek(0)  # Move pointer to start of file
            json.dump(data, db_file, indent=4)
            db_file.truncate()  # Remove remaining data

    except FileNotFoundError:
        print("db.json not found or invalid. Creating new database.")
        with open("db.json", "w") as db_file:
            data = {"lingos": []}
            json.dump(data, db_file, indent=4)

    except Exception as e:
        print(f"Error DB entries: {e}")


def clean_db(remove_duplicates=True, sort_entries=True):
    try:
        # Try loading JSON
        try:
            with open("db.json", "r", encoding="utf-8") as db_file:
                data = json.load(db_file)
                if not isinstance(data, dict):
                    print("Invalid JSON root (not an object). Resetting database.")
                    data = {}
        except (FileNotFoundError, json.JSONDecodeError):
            print("db.json not found or invalid. Creating new database.")
            data = {}

        # Ensure "lingos" exists and is a list
        if "lingos" not in data or not isinstance(data["lingos"], list):
            print("Creating empty 'lingos' list in db.json.")
            data["lingos"] = []

        if not data["lingos"]:
            print("Database is empty. Nothing to clean.")
            with open("db.json", "w", encoding="utf-8") as db_file:
                json.dump(data, db_file, indent=4, ensure_ascii=False)
            return

        seen = set()
        cleaned = []
        duplicates = 0

        # Loop over every item in the db
        for entry in data["lingos"]:
            if not isinstance(entry, dict) or len(entry) != 1:
                continue

            question, answer = next(iter(entry.items()))
            key = (question.strip(), answer.strip())

            if key not in seen:
                seen.add(key)
                cleaned.append(entry)
            else:
                duplicates += 1

        if sort_entries:
            cleaned.sort(key=lambda e: next(iter(e.keys())).lower())

        data["lingos"] = cleaned

        with open("db.json", "w", encoding="utf-8") as db_file:
            json.dump(data, db_file, indent=4, ensure_ascii=False)

        print(f"Database cleaned successfully: {duplicates} duplicates removed. Total {len(cleaned)} entries remain.")

    except Exception as e:
        print(f"Error cleaning database: {e}")


def open_website(url: str):
    global driver
    try:
        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
        else:
            options.add_argument("--no-sandbox")
        # Add a common user-agent to avoid detection
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0")

        driver = webdriver.Firefox(options=options)
        driver.get(url)

    except Exception as e:
        print(f"Error opening website: {e}")
        if driver:
            driver.quit()
        raise


def wait_for_element(by_strategy, value, timeout=10, condition=EC.presence_of_element_located):
    time.sleep(FORCE_WAIT_SEC)
    try:
        return WebDriverWait(driver, timeout).until(condition((by_strategy, value)))
    except Exception as e:
        print(f"Error waiting for element '{value}': {e}")
        raise


def click_enter_button_only(timeout: int = 5):
    time.sleep(FORCE_WAIT_SEC)
    try:
        enter_button = wait_for_element(By.ID, "enterBtn", timeout, EC.element_to_be_clickable)
        enter_button.click()
        print("Clicked the Enter button")
    except Exception as e:
        print(f"Error clicking Enter button: {e}")
        raise


def add_db(question: str, answer: str):
    time.sleep(FORCE_WAIT_SEC)
    question_str = question.text if hasattr(question, 'text') else str(question)
    answer_str = answer.text if hasattr(answer, 'text') else str(answer)
    new_entry = {question_str: answer_str}
    print(f"Adding to DB: {new_entry}")

    try:
        with open("db.json", "r+") as db_file:
            data = json.load(db_file)
            data["lingos"].append(new_entry)
            db_file.seek(0)  # Move pointer to start of file
            json.dump(data, db_file, indent=4)
            db_file.truncate()  # Remove existing data

    except FileNotFoundError:
        with open("db.json", "w") as db_file:
            data = {"lingos": [new_entry]}
            json.dump(data, db_file, indent=4)

    except Exception as e:
        print(f"Error adding to DB: {e}")


def query_db(question: str):
    time.sleep(FORCE_WAIT_SEC)
    question_str = question.text if hasattr(question, 'text') else str(question)

    try:
        with open("db.json", "r") as db_file:
            data = json.load(db_file)
            for entry in data.get("lingos", []):
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


def scrape_translations(timeout: int=3):
    # Assuming the lessons is in a loaded state
    time.sleep(FORCE_WAIT_SEC)

    driver.back()
    
    try:
        wordsets_button = wait_for_element(By.ID, "menu-big-item-icon-1", timeout, EC.element_to_be_clickable)
        wordsets_button.click()
        print("Clicked the wordsets button")
    except Exception as e:
        print(f"Error clicking wordsets button: {e}")
        raise

    chapter_link_locator = (By.CSS_SELECTOR, 'a[href^="/student-confirmed/wordset/"]')
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(chapter_link_locator)
        )
        print("Found chapter links on the page.")
    except TimeoutException:
        print("Error: Could not find any chapter links within the time limit.")
    
    chapter_elements = driver.find_elements(*chapter_link_locator)
    chapter_urls = [element.get_attribute('href') for element in chapter_elements] # Get all urls with translations in one list

    # We need to remove the duplicates, since it's the easiest way to only have one chapter in the db
    unique_urls = list(dict.fromkeys(chapter_urls))
    print("Removed duplicates in chapter_urls")

    for i, url in enumerate(unique_urls):
        print(f"Chapter url: {url}")

        # Go into that section
        driver.get(url)

        # Define locators
        container_locator = (By.CSS_SELECTOR, "div.card.rounded-3")
        translation1_locator = (By.CSS_SELECTOR, ".flashcard-border-end")
        translation2_locator = (By.CSS_SELECTOR, ".flashcard-border-start")

        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(container_locator)
            )
            print("Flashcard items found.")
            containers = driver.find_elements(*container_locator)
            print(f"Found {len(containers)} items to process.")

            for i, container in enumerate(containers):
                try:
                    element1 = container.find_element(*translation1_locator)
                    element2 = container.find_element(*translation2_locator)
    
                    # Extract the text and clean it up
                    element1 = element1.text.strip()
                    element2 = element2.text.strip()

                    # Add the translation in two ways to the db
                    add_db(element1, element2)
                    add_db(element2, element1)
            
                    print(f"Item {i + 1}: OK")

                except NoSuchElementException:
                    print("Could not locate elements in containers")
                    continue

        except TimeoutException:
            print("Error: Timed out while waiting for containers")

        driver.get("https://lingos.pl/student-confirmed/wordsets")

    clean_db(True, True)
    driver.get("https://lingos.pl/student-confirmed/group")

    wait = WebDriverWait(driver, 20)
    lesson_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "UCZ SIĘ")))
    lesson_button.click()


def translate_without_word():
    time.sleep(FORCE_WAIT_SEC)

    # Get the question text from the page
    try:
        question_content_element = wait_for_element(By.ID, "flashcard_main_text", 10, EC.visibility_of_element_located)
        question_text = question_content_element.text.strip()[:100]  # Use .strip() for clean comparison
        print(f"To translate: {question_text}")
    except Exception as e:
        print(f"Could not get question content: {e}")
        return  # Exit if we can't get the question

    # Query the local database for a translation
    translation_from_db = query_db(question_text)
    translation_to_enter = None

    # Handle cases: translation not found vs. found
    if translation_from_db is None:
        print("Translation not in DB. Revealing answer on page.")
        try:
            # Click Enter to reveal the translation
            click_enter_button_only(5)
            translation_content_element = wait_for_element(By.ID, "flashcard_error_correct", 5, EC.visibility_of_element_located)
            translation_on_page = translation_content_element.text.strip()[:500]

            # Add the new translation to the DB and prepare to enter it
            add_db(question_text, translation_on_page)
            print(f"Translation from page: {translation_on_page}")
            translation_to_enter = translation_on_page

        except Exception as e:
            print(f"Could not get translation from page after click: {e}")
            try:
                print("Attempting to click Enter to move past failed translation retrieval.")
                click_enter_button_only(5)
                click_enter_button_only(5)
            except Exception as ex:
                print(f"Failed to click Enter after translation retrieval error: {ex}")
            return  # Exit if we can't get the translation

        # Click Enter to dismiss the correction and proceed to the answer input box
        print("Clicking Enter to dismiss correction/proceed to answer input if needed.")
        click_enter_button_only(5)
    else:
        chance = random.uniform(0.0, CHANCE_OF_PASSING)
        print(f"Chance: {chance}")
        if chance >= 1:
            # If the code's randomness chooses to fail this task, enter an empty string
            translation_to_enter = ""
            print(f"Using an empty translation")
        else:
            # If translation was found in the DB, use it
            translation_to_enter = translation_from_db
            print(f"Using translation from DB: {translation_to_enter}")

    # Enter the translation into the answer box
    try:
        answer_box = wait_for_element(By.ID, "flashcard_answer_input", 10, EC.element_to_be_clickable)
        if not answer_box.is_displayed() or not answer_box.is_enabled():
            print("Answer box is not displayed or enabled, assuming auto-corrected or moved on.")
            click_enter_button_only(5)
            return
        answer_box.send_keys(translation_to_enter)
        print("Translation entered")

    except TimeoutException:
        print(f"Timeout: Answer box 'flashcard_answer_input' not found or not clickable.")
        print("Attempting to click Enter to move to next card, as input wasn't possible.")
        try:
            click_enter_button_only(5)
            click_enter_button_only(5)  # Try double-click to ensure progression
        except Exception as ex:
            print(f"Failed to click Enter after answer box issue: {ex}")
        return

    except Exception as e:
        print(f"Error entering translation into answer box: {e}")
        return

    # Submit the answer and move to the next card
    print("Clicking Enter to submit answer.")
    click_enter_button_only(5)

    try:
        # Check if the correction/feedback element appears
        wait_for_element(By.ID, "flashcard_error_correct", 5, EC.visibility_of_element_located)
        print("Correction/feedback visible.")
    except TimeoutException:
        print(f"Did not find correction/feedback element ('flashcard_error_correct') after submitting answer within 5s. Page might have moved on or different feedback.")
    except Exception as e:
        print(f"Error checking for correction/feedback: {e}")

    print("Clicking Enter to move to the next card.")
    click_enter_button_only(5)


def new_word(native: str, foreign: str):
    time.sleep(FORCE_WAIT_SEC)
    add_db(foreign, native)
    print("Clicking Enter to dismiss new word card.")
    click_enter_button_only(5)


def main():
    global driver
    global LESSON_COUNT
    global AUTOMATED_LOGIN

    try:
        open_website("https://lingos.pl")

        # --- Automated login ---
        if AUTOMATED_LOGIN:
            print(f"Automated login turned on, will do {LESSON_COUNT} lessons.")
            login_button = wait_for_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-sm.fs-sm.order-lg-3.d-none.d-lg-inline-flex", 20, EC.element_to_be_clickable)
            login_button.click()

            decline_button = wait_for_element(By.ID, "CybotCookiebotDialogBodyButtonDecline", 20, EC.element_to_be_clickable)
            decline_button.click()

            time.sleep(1)  # The website takes time to register the cookie preference

            email_field = driver.find_element(By.NAME, "login")
            password_field = driver.find_element(By.NAME, "password")
            login_button = driver.find_element(By.ID, "submit-login-button")

            email_field.send_keys(EMAIL)
            password_field.send_keys(PASSWORD)
            login_button.click()

            wait = WebDriverWait(driver, 20)
            lesson_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "UCZ SIĘ")))
            lesson_button.click()
        else:
            print("Log in to the website and go to the learning page (e.g., 'Learn' section).")
            input("Press ENTER after the lesson is loaded: ")

        scrape_translations(10)
        # --- Lesson Loop ---
        lessons_to_do = LESSON_COUNT if AUTOMATED_LOGIN else 1
        for i in range(lessons_to_do):
            if AUTOMATED_LOGIN:
                print(f"\n--- Starting lesson {i + 1} of {lessons_to_do} ---")

            # --- Task loop ---
            while True:
                # Define conditions to wait for
                flashcard_title_condition = EC.visibility_of_element_located((By.ID, "flashcard_title_text"))  # Translate task
                new_word_span_condition = EC.visibility_of_element_located((By.XPATH, "//span[normalize-space(text())='Nowe słowo!']"))  # New word
                lesson_ended_condition = EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "UCZ SIĘ"))  # Lesson finished indicator

                try:
                    print("\nWaiting for a task, new word, or lesson end (max 20s)")
                    found_element = WebDriverWait(driver, 20).until(
                        EC.any_of(flashcard_title_condition, new_word_span_condition, lesson_ended_condition)
                    )
                    element_text = found_element.text.strip().upper()

                    # Check if the lesson has ended
                    if "UCZ SIĘ" in element_text and found_element.is_displayed():
                        print("Lesson has ended. Returning to dashboard.")
                        break  # Exit the inner while loop to finish this lesson

                    # Identify and handle the current card type
                    if found_element.get_attribute("id") == "flashcard_title_text":
                        question_type_text = found_element.text.strip()[:100]
                        print(f"Current Task identified: '{question_type_text}'")
                        if question_type_text == "Przetłumacz:":
                            print("Type: translate")
                            translate_without_word()
                        else:
                            print(f"Unknown task type: '{question_type_text}'. Stopping...")
                            sys.exit(1)

                    elif found_element.tag_name == "span" and "NOWE SŁOWO!" in element_text:
                        print("A new word found.")
                        foreign = wait_for_element(By.ID, "new_teacher_main_text", 5, EC.visibility_of_element_located)
                        foreign_text = foreign.text.strip()[:500]
                        native = wait_for_element(By.ID, "new_teacher_additional_text", 5, EC.visibility_of_element_located)
                        native_text = native.text.strip()[:500]
                        new_word(native_text, foreign_text)  # Call new_word with collected data

                    else:
                        print(f"Unexpected element found or state: Tag={found_element.tag_name}, ID={found_element.get_attribute('id')}, Text='{found_element.text.strip()[:50]}'")
                        print("Continuing to next check...")

                except TimeoutException:
                    print("Timeout waiting for task (20s). Assuming lesson/session finished.")
                    break  # Exit inner loop if no element appears after 20 seconds
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    print(f"Element issue (stale/not found) in main loop: {e}. Retrying...")
                    time.sleep(1)  # Short delay before retrying
                    continue
                except Exception as e:
                    print(f"An unexpected error occurred in the main loop: {e}")
                    break  # Exit inner loop for other errors

            # --- Check and start next lesson ---
            if AUTOMATED_LOGIN and (i + 1) < lessons_to_do:
                print("Starting the next lesson...")
                try:
                    next_lesson_button = wait_for_element(By.PARTIAL_LINK_TEXT, "UCZ SIĘ", 20, EC.element_to_be_clickable)
                    next_lesson_button.click()
                except Exception as e:
                    print(f"Could not start the next lesson. Stopping. Error: {e}")
                    break  # Exit the outer for loop

    except Exception as e:
        print(f"An error occurred in main execution: {e}")

    finally:
        if driver:
            print("Quitting browser...")
            driver.quit()
            print("Browser closed.")


if __name__ == "__main__":
    try:
        if CLEAR_DB_BEFORE_SESSION:
            remove_db()
        else:
            clean_db(True, True)

        main()
    except Exception as e:
        print(f"An error occurred in the script's main execution block: {e}")
    finally:
        if driver and driver.session_id:  # Check if session is still active
            driver.quit()
