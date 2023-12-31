from fuzzywuzzy import process
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from django.conf import settings
import re, os


import imaplib
import email


def import_text_file(file_name):
    # Define the path to the text_files directory
    file_path = os.path.join(os.path.dirname(__file__), "help_text", file_name)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def replace_placeholder(text, business_name):
    return text.format(business_name)


def replace_placeholders(text, *args):
    return text.format(*args)


def select_checkboxes(driver):
    # Find all elements with the CSS selector 'div.n-checkbox'
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "div.n-checkbox")

    # Iterate over the checkboxes
    for checkbox in checkboxes:
        # Get the class attribute of the checkbox
        class_attribute = checkbox.get_attribute("class")

        # Check if it only has 'n-checkbox' and not 'n-checkbox--checked'
        if "n-checkbox--checked" not in class_attribute:
            # If it's not checked, click on the checkbox
            checkbox.click()
            print("\nCheckbox clicked.")
        else:
            # If it's already checked, skip it
            print("\nCheckbox is already checked. Skipping.")


def scroll_and_select(driver, container_element, desired_option_locator, timeout=3):
    """
    Scroll through a container element until a desired option becomes visible and then select it.

    Parameters:
    - driver: Selenium WebDriver instance
    - container_element: The WebElement representing the container with a scrollbar
    - desired_option_locator: Locator for the desired option within the container
    - timeout: Maximum time to wait for the presence of the desired option (default is 3 seconds)
    """
    item_visible = False
    prev_scroll_position = -1

    while not item_visible:
        current_scroll_position = driver.execute_script(
            "return arguments[0].scrollTop;", container_element
        )
        driver.execute_script(
            "arguments[0].scrollTop += arguments[0].offsetHeight;", container_element
        )

        if current_scroll_position == prev_scroll_position:
            break

        prev_scroll_position = current_scroll_position

        try:
            item = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, desired_option_locator))
            )
            item_visible = True
        except:
            pass  # Continue scrolling if the item is not yet visible

    if item_visible:
        return item
    else:
        return None


def otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD):
    # Connect to the mail server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login to your account
    mail.login(USER_EMAIL, USER_EMAIL_PASSWORD)

    # Select the mailbox you want to check
    mail.select("inbox")

    # Search for specific mail by sender
    resp, items = mail.uid(
        "search", None, '(HEADER From "do-not-reply@donotreply.leadconnectorhq.com")'
    )
    items = items[0].split()

    # Get the latest email
    latest = items[-1]

    resp, data = mail.uid("fetch", latest, "(BODY[TEXT])")

    raw_email = data[0][1].decode("utf-8")

    email_message = email.message_from_string(raw_email)

    # Find the OTP
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode(
                "utf-8"
            )  # Decode the bytes to a string using the appropriate encoding
            for line in body.splitlines():
                if "Your login security code:" in line:
                    otp = line.split(":")[-1].strip()
                    break

    for idx, digit in enumerate(list(otp)):
        input = driver.find_elements(
            By.XPATH, '//input[@type="number"][@maxlength="1"]'
        )[idx]
        input.send_keys(digit)
    confirm_code_button = driver.find_element(
        By.XPATH, '//button[contains(text(), "Confirm Code")]'
    )
    confirm_code_button.click()

    return otp


def buy_phone_number(
    driver,
    actions,
    SUB_ACCOUNT,
    NUMBER_DIGITS,
    USER_EMAIL,
    USER_EMAIL_PASSWORD,
    EMAIL,
    EMAIL_PASSWORD,
):
    # Navigate to the login page

    print()
    print("Loading site...")
    driver.get("https://app.thefollowupagency.com/")

    wait = WebDriverWait(driver, 20)

    # Find the username and password input fields and the submit button
    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(
        By.XPATH, '//button[contains(text(), "Sign in")]'
    )

    # Enter your email and password
    username_input.send_keys(EMAIL)
    password_input.send_keys(EMAIL_PASSWORD)

    print()
    print("Entered login details successfully.")

    # Submit the form
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    submit_button.click()

    try:
        print()
        print("Sending OTP...")
        wait = WebDriverWait(driver, 80)
        send_code_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Send Security Code")]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
        send_code_button.click()

        time.sleep(10)  # wait for the OTP to be sent

        # Now handle the OTP
        otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD)

        print()
        print("OTP verified successfully")

        print()
        print("Login successful!")

        # Click on switch account to select a sub account
        switch_account = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".hl_location-text .hl_switcher-loc-name")
            )
        )
        switch_account.click()

        print()
        print("Select account section displayed")

        # Wait for the list container to appear
        list_container = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#location-switcher-sidbar-v2 > div.hl_v2-location_switcher",
                )
            )
        )

        # Wait for the list of items to load (adjust the timeout and locator as needed)
        wait = WebDriverWait(driver, 180)
        list_item = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "hl_account"))
        )

        # Search for sub account
        search_input = list_container.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Search for a sub-account"]'
        )
        search_input.send_keys(SUB_ACCOUNT)

        # Wait for filtering of sub accounts
        time.sleep(5)

        try:
            # Select the first sub account
            wait = WebDriverWait(driver, 180)
            list_item = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "hl_account"))
            )
            actions.move_to_element(list_item)
            actions.click()
            actions.perform()
        except Exception as e:
            raise Exception(f"Sub account not found {e}")

        # Click on settings
        settings = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#sb_settings"))
        )
        actions.move_to_element(settings)
        actions.click()
        actions.perform()

        # Select Phone Numbers form the settings options
        phone_number = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#sb_phone-number"))
        )
        actions.move_to_element(phone_number)
        actions.click()
        actions.perform()

        # Click on Add Number"
        add_number = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, " #btn-add-number > span")
            )
        )
        actions.move_to_element(add_number)
        actions.click()
        actions.perform()

        # Click on Add Phone Number
        add_phone_number = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#dropdown-add-number > div:nth-child(1) > div > div.flex.flex-col.gap-0 > div.text-gray-900.hl-text-sm-medium",
                )
            )
        )
        actions.move_to_element(add_phone_number)
        actions.click()
        actions.perform()

        time.sleep(10)

        # Click Filter to filter phone number
        filter_phone_number = driver.find_element(
            By.CSS_SELECTOR, "#PendoButton\.FILTER > span"
        )
        filter_phone_number.click()

        # Enter the first three phone number digits to filter with
        number_input = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#filter > div.n-input-wrapper > div.n-input__input > input",
                )
            )
        )
        number_input.send_keys(NUMBER_DIGITS)

        # Select the 'Match to' filter option
        match_option = driver.find_elements(By.XPATH, "//*[@id='select-provider']")

        match_option[1].click()
        option = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'n-base-select-option') and text()='First part of number']",
        )
        option.click()

        # Click on apply to filter the phone numbers
        apply_button = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#btn-apply > span > div")
            )
        )
        actions.move_to_element(apply_button)
        actions.click()
        actions.perform()

        time.sleep(10)

        # Select a number to buy
        # Find all radio buttons
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        number = None
        if len(radio_buttons) > 0:
            # Click the first radio button
            radio_buttons[0].click()
            # Create a list to store phone numbers
            number = driver.find_element(
                By.CSS_SELECTOR,
                "#modal-buy-number-step-1 > div:nth-child(2) > div > div.ghl-table-container > div.n-data-table.n-data-table--bottom-bordered.n-data-table--single-line > div > div > div.n-data-table-base-table-body.n-scrollbar > div.v-vl > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div > div.shrink-1.mr-2.text-gray-900.hl-text-sm-medium",
            )

        else:
            # Click Filter to filter phone number
            filter_phone_number = driver.find_element(
                By.CSS_SELECTOR, "#PendoButton\.FILTER > span"
            )
            filter_phone_number.click()

            reset = driver.find_element(
                By.CSS_SELECTOR,
                "span.n-button__content > div.text-error-700.hl-text-sm-medium",
            )
            reset.click()

            time.sleep(2)

            radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")

            # Click the first radio button
            radio_buttons[0].click()
            # Create a list to store phone numbers
            number = driver.find_element(
                By.CSS_SELECTOR,
                "#modal-buy-number-step-1 > div:nth-child(2) > div > div.ghl-table-container > div.n-data-table.n-data-table--bottom-bordered.n-data-table--single-line > div > div > div.n-data-table-base-table-body.n-scrollbar > div.v-vl > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div > div.shrink-1.mr-2.text-gray-900.hl-text-sm-medium",
            )

        # Buy  a number
        buy_number = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn-move-numbers"))
        )
        actions.move_to_element(buy_number)
        actions.click()
        actions.perform()

        print()
        print(f"Number {number.text} bought successfully.")
        time.sleep(5)

        return number.text
        # input("Press Enter to exit the script and close the browser...")

    except Exception as e:
        print()
        print(f"Operation failed. Error: {e}")


def buy_phone_number_with_retries(business_name, business_phone, max_retries=3):
    # CHROME_DRIVER_PATH = "path/to/chromedriver"

    SUB_ACCOUNT = business_name
    NUMBER_DIGITS = extract_area_code(business_phone)

    # For getting the OTP from emails
    USER_EMAIL = settings.USER_EMAIL
    USER_EMAIL_PASSWORD = settings.USER_EMAIL_PASSWORD

    # For logining into FollowUpAgency
    EMAIL = settings.EMAIL
    EMAIL_PASSWORD = settings.EMAIL_PASSWORD

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.binary_location = CHROME_DRIVER_PATH
    driver = webdriver.Chrome(options=chrome_options)
    # Create ActionChains object
    actions = ActionChains(driver)
    phone = None
    for retry in range(max_retries):
        try:
            phone = buy_phone_number(
                driver,
                actions,
                SUB_ACCOUNT,
                NUMBER_DIGITS,
                USER_EMAIL,
                USER_EMAIL_PASSWORD,
                EMAIL,
                EMAIL_PASSWORD,
            )
            if phone is not None:
                break
        except Exception as e:
            print()
            print(f"Operation failed with exception: {e}")
            if retry < max_retries - 1:
                print()
                print("Retrying...")
                time.sleep(5)
            else:
                raise Exception(f"Maximum retries reached")

    if phone is not None:
        print("\ndone....")
        driver.quit()
        return phone


def a2p_ein_business_reg(driver, actions, sub_user):
    print()
    print("On business details page")

    ## Business Details
    classic_inputs = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")
    # Legal Business Name
    legal_business_name_input = classic_inputs[0]
    legal_business_name_input.click()
    legal_business_name_input.clear()
    time.sleep(0.5)
    legal_business_name_input.send_keys(Keys.BACK_SPACE * 50)
    legal_business_name_input.send_keys(sub_user.legal_business_name)
    print("\nEntered business name")

    # Business Type (Select field)
    driver.find_element(By.ID, "SelectBusinessType").click()
    time.sleep(2)
    business_types = driver.find_elements(
        By.CSS_SELECTOR, "div.n-base-select-option__content"
    )
    for i, bus in enumerate(business_types):
        if sub_user.business_type == bus.text:
            bus.click()
    print()
    print("Selected business type")

    # Business Registration ID Type (Select field, select the first option)
    driver.find_element(By.ID, "SelectBusinessRegistrationType").click()
    time.sleep(2)
    business_registration_ids = driver.find_elements(
        By.CSS_SELECTOR, "div.n-base-select-option__content"
    )
    business_registration_ids[5].click()
    print()
    print("Selected business registration type")

    # Business Registration Number
    business_registration_number_input = classic_inputs[1]
    business_registration_number_input.click()
    business_registration_number_input.clear()
    time.sleep(0.5)
    business_registration_number_input.send_keys(Keys.BACK_SPACE * 50)
    business_registration_number_input.send_keys(sub_user.ein)
    print("\nEntered business number")

    # Business Industry (Select field)
    # Scrollable container that holds the options
    business_industries_element = driver.find_element(By.ID, "SelectBusinessIndustry")
    business_industries_element.click()
    time.sleep(2)

    # Get all the loaded options
    business_industries_list = driver.find_elements(
            By.CSS_SELECTOR, "div.n-virtual-list.v-vl"
        )[2]

    actions.move_to_element(business_industries_list)

    desired_option_locator = f"//div[contains(@class, 'n-base-select-option__content') and contains(text(), '{sub_user.industry}')]"

    selected_option = scroll_and_select(
        driver, business_industries_list, desired_option_locator
    )
    if selected_option:
        actions = ActionChains(driver)
        actions.move_to_element(selected_option)
        actions.click()
        actions.perform()
        print(f"\nEntered business industry: {selected_option.text}")
    else:
        desired_option_locator = f"//div[contains(@class, 'n-base-select-option__content') and contains(text(), 'Engineering')]"
        selected_option = scroll_and_select(
            driver, business_industries_list, desired_option_locator
        )
        if selected_option:
            actions = ActionChains(driver)
            actions.move_to_element(selected_option)
            actions.click()
            actions.perform()
            print("\nIndustry doesn't match, selected Engineering.....")

    # Business Email
    business_email_input = classic_inputs[2]
    business_email_input.click()  # Focus on the input field
    business_email_input.clear()  # Clear the field
    time.sleep(0.5)  # Short delay to allow the field to clear
    business_email_input.send_keys(
        Keys.BACK_SPACE * 50
    )  # Ensure the field is cleared by sending backspace
    business_email_input.send_keys(sub_user.business_email)
    print("\nEntered business email")

    # Website URL
    website_url_input = classic_inputs[3]
    website_url_input.click()
    website_url_input.clear()
    time.sleep(0.5)
    website_url_input.send_keys(Keys.BACK_SPACE * 50)
    website_url_input.send_keys(sub_user.website)
    print("\nEntered business url")

    # Business Region of Operations (Select field)
    # Find all checkbox elements for Business Region of Operations
    region_checkboxes = driver.find_elements(By.CSS_SELECTOR, "div.n-checkbox")

    # Create a list of region labels from the checkbox elements
    region_labels = [
        checkbox.find_element(By.CSS_SELECTOR, "span.n-checkbox__label").text
        for checkbox in region_checkboxes
    ]

    # Business Region of Operations
    # Click the checkboxes based on the sub_user's business region operations
    selected_regions = sub_user.business_region_operation.split(" ")
    for checkbox, label in zip(region_checkboxes, region_labels):
        # If the label is in sub_user's business regions, or if none are and label is 'USA & Canada', click the checkbox
        if label in selected_regions or (
            not any(region in selected_regions for region in region_labels)
            and label == "USA & Canada"
        ):
            checkbox.click()

    print()
    print("Selected business region of operations")

    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "button.n-button.n-button--primary-type.n-button--medium-type",
            )
        )
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()
    print("\nClicked continue")

    time.sleep(5)


def a2p_ein_business_add(driver, sub_user):
    ## Business Street Address

    classic_inputs = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

    street_address = classic_inputs[0]
    street_address.click()
    street_address.clear()
    time.sleep(0.5)
    street_address.send_keys(Keys.BACK_SPACE * 50)
    street_address.send_keys(sub_user.address)
    print("\nBusiness Street Address")

    ## Business City
    city = classic_inputs[1]
    city.click()
    city.clear()
    time.sleep(0.5)
    city.send_keys(Keys.BACK_SPACE * 50)
    city.send_keys(sub_user.city)
    print("\nBusiness City")

    ## Business zip code
    postal = classic_inputs[2]
    postal.click()
    postal.clear()
    time.sleep(0.5)
    postal.send_keys(Keys.BACK_SPACE * 50)
    postal.send_keys(sub_user.zip_code)
    print("\nBusiness Zip Code")

    # Continue to the next form
    driver.find_element(
        By.CSS_SELECTOR, "button.n-button.n-button--primary-type"
    ).click()
    print()
    print("Clicked continue ")

    time.sleep(5)


def a2p_ein_business_contact(driver, sub_user):
    time.sleep(1)
    ## First Name

    classic_inputs = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

    first_name = classic_inputs[0]
    first_name.click()
    first_name.clear()
    time.sleep(0.5)
    first_name.send_keys(Keys.BACK_SPACE * 50)
    first_name.send_keys(sub_user.first_name)
    print("\nFirst Name entered")

    ## Last Name
    last_name = classic_inputs[1]
    last_name.click()
    last_name.clear()
    time.sleep(0.5)
    last_name.send_keys(Keys.BACK_SPACE * 50)
    last_name.send_keys(sub_user.last_name)
    print("\nLast Name entered")

    ## Contact Email
    contact_email = classic_inputs[2]
    contact_email.click()
    contact_email.clear()
    time.sleep(0.5)
    contact_email.send_keys(Keys.BACK_SPACE * 50)
    contact_email.send_keys(sub_user.contact_email)
    print("\nContact Email entered")

    ## Contact Phone
    contact_phone = classic_inputs[3]
    contact_phone.click()
    contact_phone.clear()
    time.sleep(0.5)
    contact_phone.send_keys(Keys.BACK_SPACE * 50)
    contact_phone.send_keys(sub_user.contact_phone)
    print("\nContact Phone entered")

    ## Job position
    driver.find_element(By.CSS_SELECTOR, "div#SelectCountry").click()
    driver.find_elements(By.CSS_SELECTOR, "div.n-base-select-option__content")[
        6
    ].click()

    time.sleep(5)

    job_position = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")[4]
    job_position.click()
    job_position.clear()
    time.sleep(0.5)
    job_position.send_keys(Keys.BACK_SPACE * 50)
    job_position.send_keys(sub_user.job_position)
    print("\nJob position entered")

    # Continue to the next form
    driver.find_element(
        By.CSS_SELECTOR, "button.n-button.n-button--primary-type"
    ).click()
    print()
    print("Clicked continue ")

    time.sleep(5)


def a2p_ein_business_use_case(driver, actions):
    print("\nEntering Brand details")
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "div.n-checkbox-box__border").click()
    print("\nChecked agreement box")
    time.sleep(2)

    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "button.n-button.n-button--primary-type.n-button--medium-type",
            )
        )
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()
    print("\nClicked continue ")

    time.sleep(5)


def a2p_ein_campaign_details(driver, actions, sub_user, case1, case2, case3):
    print("\nEntering Campaign details")

    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "div#SelectCampaignUsecase").click()
    time.sleep(3)

    campaign_use_case = driver.find_elements(
        By.CSS_SELECTOR, "div.n-base-select-option__content"
    )
    campaign_use_case[0].click()

    print("\nCampaign use case selected")

    classic_inputs = driver.find_elements(
        By.CSS_SELECTOR, "textarea.n-input__textarea-el"
    )

    # Importing text file contents
    use_case_des = import_text_file(case1)
    sample_msg_1 = import_text_file(case2)
    sample_msg_2 = import_text_file(case3)

    # Fill the textareas with the content, replacing placeholders with business name
    classic_inputs[0].click()
    classic_inputs[0].clear()
    time.sleep(1)
    classic_inputs[0].send_keys(Keys.BACK_SPACE * 150)
    classic_inputs[0].send_keys(use_case_des)
    print("\nUse case description entered")

    classic_inputs[1].click()
    classic_inputs[1].clear()
    time.sleep(1)
    classic_inputs[1].send_keys(Keys.BACK_SPACE * 150)
    classic_inputs[1].send_keys(
        replace_placeholder(sample_msg_1, sub_user.business_name)
    )
    print("\nSample message 1 entered")

    classic_inputs[2].click()
    classic_inputs[2].clear()
    time.sleep(1)
    classic_inputs[2].send_keys(Keys.BACK_SPACE * 150)
    classic_inputs[2].send_keys(
        replace_placeholder(sample_msg_2, sub_user.business_name)
    )
    print("\nSample message 2 entered")

    # select the checkbox
    select_checkboxes(driver)

    time.sleep(5)
    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                "button.n-button.n-button--primary-type.n-button--medium-type",
            )
        )
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()
    print("\nClicked continue")

    time.sleep(5)


def a2p_ein_user_content(driver, sub_user, case1, case2, case3):
    time.sleep(2)
    print("\nEntering User Content details")

    # Assuming there are text areas to fill in, just like in the previous function
    # We will import the content of the text files and fill in the text areas, replacing placeholders
    user_contents = driver.find_elements(
        By.CSS_SELECTOR, "textarea.n-input__textarea-el"
    )

    # Fill the first textarea with the contact consent message, replacing placeholders
    contact_consent = import_text_file(case1)
    # user_contents[0].click()
    user_contents[0].clear()
    time.sleep(1)
    user_contents[0].send_keys(Keys.BACK_SPACE * 150)
    user_contents[0].send_keys(
        replace_placeholders(
            contact_consent,
            sub_user.website,
            sub_user.business_name,
            sub_user.business_phone,
        )
    )
    print("\nContact consent entered")

    # Fill the second textarea with keywords, no placeholders to replace
    keywords = import_text_file(case2)
    # user_contents[1].click()
    user_contents[1].clear()
    time.sleep(1)
    user_contents[1].send_keys(Keys.BACK_SPACE * 150)
    user_contents[1].send_keys(keywords)
    print("\nKeywords entered")

    # Fill the third textarea with the opt-in message, replacing placeholders
    opt_in_msg = import_text_file(case3)
    # user_contents[2].click()
    user_contents[2].clear()
    time.sleep(1)
    user_contents[2].send_keys(Keys.BACK_SPACE * 150)
    user_contents[2].send_keys(
        replace_placeholders(
            opt_in_msg,
            sub_user.business_name,
            sub_user.website,
            sub_user.business_phone,
        )
    )
    print("\nOpt in message entered")

    time.sleep(5)

    # Submit to register
    driver.find_element(By.CSS_SELECTOR, "button.n-button.n-button--primary-type").click()
    print()
    print("Clicked continue ")

    time.sleep(5)


# NO EIN
def a2p_no_ein_bus_details(driver, sub_user):
    time.sleep(3)

    print("\nEntering Business details")

    business_name = driver.find_element(By.CSS_SELECTOR, "input.n-input__input-el")
    business_name.click()
    business_name.clear()
    time.sleep(0.5)
    business_name.send_keys(Keys.BACK_SPACE * 50)
    business_name.send_keys(sub_user.business_name)
    print("\nBusiness Name entered")

    time.sleep(1)

    # Continue to the next form
    driver.find_element(
        By.CSS_SELECTOR, "button.n-button.n-button--primary-type"
    ).click()
    print()
    print("Clicked continue ")

    time.sleep(3)


def a2p_no_ein_bus_address(driver, sub_user):
    print("\nEntering Business Address")

    classic_inputs = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

    street_address = classic_inputs[0]
    street_address.click()
    street_address.clear()
    time.sleep(0.5)
    street_address.send_keys(Keys.BACK_SPACE * 50)
    street_address.send_keys(sub_user.address)
    print("\nBusiness address entered")

    city = classic_inputs[1]
    city.click()
    city.clear()
    time.sleep(0.5)
    city.send_keys(Keys.BACK_SPACE * 50)
    city.send_keys(sub_user.city)
    print("\nCity entered")

    zip_code = classic_inputs[2]
    zip_code.click()
    zip_code.clear()
    time.sleep(0.5)
    zip_code.send_keys(Keys.BACK_SPACE * 50)
    zip_code.send_keys(sub_user.zip_code)
    print("\nZip code entered")

    time.sleep(1)

    # Continue to the next form
    driver.find_element(
        By.CSS_SELECTOR, "button.n-button.n-button--primary-type"
    ).click()
    print()
    print("Clicked continue ")

    time.sleep(3)


def a2p_no_ein_brand_details(driver, sub_user):
    print("\nEntering Brand Details")

    classic_inputs = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

    business_name = classic_inputs[0]
    business_name.click()
    business_name.clear()
    time.sleep(0.5)
    business_name.send_keys(Keys.BACK_SPACE * 50)
    business_name.send_keys(sub_user.business_name)
    print("\nBusiness brand name entered")

    # Business Industry (Select field)
    business_industries_element = driver.find_element(By.ID, "SelectBusinessIndustry")
    business_industries_element.click()
    time.sleep(2)

    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.n-scrollbar")

    # Set the initial scroll position and the amount to scroll each time
    scroll_increment = 50  # The amount of pixels to scroll each time
    scroll_position = 0  # Initial scroll position

    # Get the current scrollHeight of the content
    scroll_height = driver.execute_script(
        "return arguments[0].scrollHeight", scrollable_div
    )
    # Keep scrolling in increments until the bottom is reached
    while scroll_position < scroll_height:
        # Scroll down in the div
        driver.execute_script(
            "arguments[0].scrollTop = arguments[1]", scrollable_div, scroll_position
        )

        # Wait a bit for potentially lazy-loaded content to load
        time.sleep(0.1)

        # Update the scroll position and scrollHeight
        scroll_position += scroll_increment
        new_scroll_height = driver.execute_script(
            "return arguments[0].scrollHeight", scrollable_div
        )

        # Check if the scrollHeight has changed due to new content being loaded and update if so
        if new_scroll_height > scroll_height:
            scroll_height = new_scroll_height
        else:
            # If no new content, break the loop as we have likely reached the bottom
            break
        print("\n", scroll_height, scroll_position, new_scroll_height)

    # Get all the loaded options
    business_industries_options = driver.find_elements(
        By.CSS_SELECTOR, "div.n-base-select-option__content"
    )

    # Search for the desired industry and click it if found
    industry_found = False
    for option in business_industries_options:
        if option.text == sub_user.industry:
            option.click()
            print(f"\nEntered business Professional: {option.text}")
            industry_found = True
            break

    # If the desired industry is not found, select 'Online'
    if not industry_found:
        for option in business_industries_options:
            if option.text == "Professional":
                option.click()
                print("\nIndustry doesn't match, selected Professional.....")
                break

    business_phone = classic_inputs[1]
    business_phone.click()
    business_phone.clear()
    time.sleep(0.5)
    business_phone.send_keys(Keys.BACK_SPACE * 50)
    business_phone.send_keys(sub_user.business_phone)
    print("\nBusiness phone entered")

    time.sleep(1)

    # Continue to the next form
    driver.find_element(
        By.CSS_SELECTOR, "button.n-button.n-button--primary-type"
    ).click()
    print()
    print("Clicked continue ")

    time.sleep(3)


def a2p_register(
    driver,
    actions,
    sub_user,
    SUB_ACCOUNT,
    USER_EMAIL,
    USER_EMAIL_PASSWORD,
    EMAIL,
    EMAIL_PASSWORD,
):
    # Navigate to the login page

    print()
    print("Loading site...")
    driver.get("https://app.thefollowupagency.com/")

    wait = WebDriverWait(driver, 20)

    # Find the username and password input fields and the submit button
    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(
        By.XPATH, '//button[contains(text(), "Sign in")]'
    )

    # Enter your email and password
    username_input.send_keys(EMAIL)
    password_input.send_keys(EMAIL_PASSWORD)

    print()
    print("Entered login details successfully.")

    # Submit the form
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    submit_button.click()

    try:
        print()
        print("Sending OTP...")
        wait = WebDriverWait(driver, 80)
        send_code_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Send Security Code")]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
        send_code_button.click()

        time.sleep(10)  # wait for the OTP to be sent

        # Now handle the OTP
        otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD)

        print()
        print("OTP verified successfully")

        print()
        print("Login successful!")

        # Click on switch account to select a sub account
        switch_account = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".hl_location-text .hl_switcher-loc-name")
            )
        )
        switch_account.click()

        print()
        print("Select account section displayed")

        # Wait for the list container to appear
        list_container = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#location-switcher-sidbar-v2 > div.hl_v2-location_switcher",
                )
            )
        )

        # Wait for the list of items to load (adjust the timeout and locator as needed)
        wait = WebDriverWait(driver, 180)
        list_item = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "hl_account"))
        )

        # Search for sub account
        search_input = list_container.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Search for a sub-account"]'
        )
        search_input.send_keys(SUB_ACCOUNT)

        # Wait for filtering of sub accounts
        time.sleep(5)

        try:
            # Select the first sub account
            wait = WebDriverWait(driver, 180)
            list_item = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "hl_account"))
            )
            actions.move_to_element(list_item)
            actions.click()
            actions.perform()
        except Exception as e:
            raise Exception(f"Sub account not found {e}")

        # Click on settings
        settings = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#sb_settings"))
        )
        actions.move_to_element(settings)
        actions.click()
        actions.perform()

        # Select Phone Numbers form the settings options
        phone_number = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#sb_phone-number"))
        )
        actions.move_to_element(phone_number)
        actions.click()
        actions.perform()

        try:
            badge = driver.find_element(By.CSS_SELECTOR, "div.hl_warning")
            button = badge.find_element(By.CSS_SELECTOR, "span.close-warning-icon")
            # Move to the close button and click on it
            actions.move_to_element(button)
            actions.click()
            actions.perform()
            print()
            print("Closed up the badge!")
        except:
            print()
            print("Badge is not showing up")

        # Wait for the visibility of the unordered list (ul) with the specified class
        ul_element = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.hl_affiliate--nav"))
        )

        time.sleep(5)

        ul_element = driver.find_element(By.CSS_SELECTOR, "ul.hl_affiliate--nav")

        # Find the link (a) within this ul that contains the text 'Trust Center'
        trust_center_link = ul_element.find_element(
            By.XPATH, ".//a[contains(text(), ' Trust Center ')]"
        )

        # Move to the Trust Center link and click on it
        actions.move_to_element(trust_center_link)
        actions.click()
        actions.perform()

        print()
        print("Loading Trust Center page....")

        # Select Phone Numbers form the settings options
        start_registration = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "button#button-action-0")
            )
        )
        actions.move_to_element(start_registration)
        actions.click()
        actions.perform()
        print()
        print("Starting registration")

        # check the radio button for registered EIN
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input.n-radio-input")
        if sub_user.has_ein:
            radio_buttons[2].click()
            print()
            print("Selected EIN radio button")

            # Continue to the next form
            _continue = WebDriverWait(driver, 180).until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.n-button.n-button--primary-type.n-button--medium-type",
                    )
                )
            )
            actions.move_to_element(_continue)
            actions.click()
            actions.perform()
            print()
            print("clicked continue")

            # business details registration
            a2p_ein_business_reg(driver, actions, sub_user)

            # business address registration
            a2p_ein_business_add(driver, sub_user)

            # business contact info
            a2p_ein_business_contact(driver, sub_user)

            # business use case
            a2p_ein_business_use_case(driver, actions)

            # Campaign details
            a2p_ein_campaign_details(
                driver,
                actions,
                sub_user,
                "use_case_des.txt",
                "sample_msg_1.txt",
                "sample_msg_2.txt",
            )

            # user consent
            a2p_ein_user_content(
                driver,
                sub_user,
                "contact_consent.txt",
                "keywords.txt",
                "opt_in_msg.txt",
            )

            time.sleep(10)
        else:
            radio_buttons[3].click()
            print()
            print("Selected NO-EIN radio button")

            # Continue to the next form
            _continue = WebDriverWait(driver, 180).until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.n-button.n-button--primary-type.n-button--medium-type",
                    )
                )
            )
            actions.move_to_element(_continue)
            actions.click()
            actions.perform()
            print()
            print("clicked continue")

            # Business details
            a2p_no_ein_bus_details(driver, sub_user)

            # Business address
            a2p_no_ein_bus_address(driver, sub_user)

            # Business contact info
            a2p_ein_business_contact(driver, sub_user)

            # Business use case
            a2p_ein_business_use_case(driver, actions)

            # business brand details
            a2p_no_ein_brand_details(driver, sub_user)

            # Campaign details
            a2p_ein_campaign_details(
                driver,
                actions,
                sub_user,
                "noein_use_case_des.txt",
                "noein_sample_msg_1.txt",
                "noein_sample_msg_2.txt",
            )

            # user consent
            a2p_ein_user_content(
                driver,
                sub_user,
                "contact_consent.txt",
                "keywords.txt",
                "opt_in_msg.txt",
            )

            time.sleep(10)

        return "done"
    except Exception as e:
        print()
        print(f"Operation failed. Error: {e}")


def a2pregister_with_retries(sub_user, max_retries=3):
    # CHROME_DRIVER_PATH = "path/to/chromedriver"

    SUB_ACCOUNT = sub_user.business_name

    # For getting the OTP from emails
    USER_EMAIL = settings.USER_EMAIL
    USER_EMAIL_PASSWORD = settings.USER_EMAIL_PASSWORD

    # For logining into FollowUpAgency
    EMAIL = settings.EMAIL
    EMAIL_PASSWORD = settings.EMAIL_PASSWORD

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("start-maximized")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.binary_location = CHROME_DRIVER_PATH
    driver = webdriver.Chrome(options=chrome_options)
    # Create ActionChains object
    actions = ActionChains(driver)
    done = False
    for retry in range(max_retries):
        try:
            x = a2p_register(
                driver,
                actions,
                sub_user,
                SUB_ACCOUNT,
                USER_EMAIL,
                USER_EMAIL_PASSWORD,
                EMAIL,
                EMAIL_PASSWORD,
            )
            if x == "done":
                done = True
                break
        except Exception as e:
            print()
            print(f"Operation failed with exception: {e}")
            if retry < max_retries - 1:
                print()
                print("Retrying...")
                time.sleep(5)
            else:
                raise Exception(f"Maximum retries reached")
    print("\ndone....")
    driver.quit()
    return done


def generate_dynamic_mapping(csv_columns, model_fields):
    mapping = {}
    for column in csv_columns:
        # Find the best match from model_fields for the current column
        best_match, score = process.extractOne(column, model_fields)
        # We only consider it a match if the score is above a certain threshold
        if score > 80:  # you can adjust this threshold as necessary
            mapping[column] = best_match
    return mapping


def extract_area_code(phone_number):
    # Removing country code if present
    if phone_number.startswith("+1"):
        phone_number = phone_number[2:]

    # Extracting the area code
    area_code = re.search(r"\d{3}", phone_number)
    if area_code:
        return area_code.group()
    else:
        return None


def find_stripe_customer_id(data):
    # Iterate through the list of custom values
    for item in data["customValues"]:
        # Check if the name matches 'Stripe Customer ID'
        if item["name"] == "Stripe Customer ID":
            # Return the ID of the matching object
            return item["id"]
    return None
