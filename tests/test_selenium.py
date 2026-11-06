import os, unittest, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
SELENIUM_URL = os.environ.get("SELENIUM_URL", "http://127.0.0.1:4444/wd/hub")

class EventRegistrationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
        cls.wait = WebDriverWait(cls.driver, 20)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_student_registration_login_event_booking_and_admin_view(self):
        d = self.driver
        email = f"selenium{int(time.time())}@example.com"

        d.get(BASE_URL + "/register")
        d.find_element(By.NAME, "name").send_keys("Selenium Student")
        d.find_element(By.NAME, "email").send_keys(email)
        d.find_element(By.NAME, "password").send_keys("TestPass123")
        d.find_element(By.CSS_SELECTOR, "button").click()
        self.wait.until(EC.url_contains("/login"))

        d.find_element(By.NAME, "email").send_keys(email)
        d.find_element(By.NAME, "password").send_keys("TestPass123")
        d.find_element(By.CSS_SELECTOR, "button").click()
        self.wait.until(EC.url_contains("/"))

        d.find_element(By.LINK_TEXT, "Register").click()
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Event registration confirmed"))

        d.get(BASE_URL + "/admin")
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Selenium Student"))
        self.assertIn(email, d.page_source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
