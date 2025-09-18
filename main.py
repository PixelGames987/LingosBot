from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
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
        try:
            question_content = driver.find_element(By.ID, "flashcard_main_text")
            if question_content:
                print(f"To translate: {question_content.text[:100]}")
            else:
                print("No body element found")
        except Exception as e:
            print(f"Error: {e}")

        




if __name__ == "__main__":
    main()
