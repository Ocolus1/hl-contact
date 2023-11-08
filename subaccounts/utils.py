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
import re


import imaplib
import email



def otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD):
    # Connect to the mail server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login to your account
    mail.login(USER_EMAIL, USER_EMAIL_PASSWORD)

    # Select the mailbox you want to check
    mail.select("inbox")

    # Search for specific mail by sender
    resp, items = mail.uid("search", None, '(HEADER From "do-not-reply@donotreply.leadconnectorhq.com")')
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
        body = body.decode('utf-8')  # Decode the bytes to a string using the appropriate encoding
        for line in body.splitlines():
            if "Your login security code:" in line:
                otp = line.split(":")[-1].strip()
                break

    
    for idx, digit in enumerate(list(otp)):
        input = driver.find_elements(By.XPATH, '//input[@type="number"][@maxlength="1"]')[idx]
        input.send_keys(digit)
    confirm_code_button = driver.find_element(By.XPATH, '//button[contains(text(), "Confirm Code")]')
    confirm_code_button.click()

    return otp


def buy_phone_number(driver, actions, SUB_ACCOUNT, NUMBER_DIGITS, USER_EMAIL, USER_EMAIL_PASSWORD, EMAIL, EMAIL_PASSWORD):
    # Navigate to the login page

    print()
    print("Loading site...")
    driver.get('https://app.thefollowupagency.com/')

    wait = WebDriverWait(driver, 20)

    # Find the username and password input fields and the submit button
    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID,"password")
    submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Sign in")]')

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
        send_code_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Send Security Code")]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
        send_code_button.click()

        time.sleep(10)    # wait for the OTP to be sent

        # Now handle the OTP
        otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD)

        print()
        print("OTP verified successfully")

        print()
        print("Login successful!")

        # Click on switch account to select a sub account
        switch_account = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".hl_location-text .hl_switcher-loc-name"))
        )
        switch_account.click()

        print()
        print("Select account section displayed")
        
        # Wait for the list container to appear
        list_container = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#location-switcher-sidbar-v2 > div.hl_v2-location_switcher"))
        )
 
        # Wait for the list of items to load (adjust the timeout and locator as needed)
        wait = WebDriverWait(driver, 180)
        list_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hl_account")))
        
        # Search for sub account
        search_input = list_container.find_element(By.CSS_SELECTOR, 'input[placeholder="Search for a sub-account"]')
        search_input.send_keys(SUB_ACCOUNT)

        # Wait for filtering of sub accounts        
        time.sleep(5)

        try:
            # Select the first sub account
            wait = WebDriverWait(driver, 180)
            list_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hl_account")))
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
            EC.visibility_of_element_located((By.CSS_SELECTOR, " #btn-add-number > span"))
        )
        actions.move_to_element(add_number)
        actions.click()
        actions.perform()  

        # Click on Add Phone Number
        add_phone_number = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#dropdown-add-number > div:nth-child(1) > div > div.flex.flex-col.gap-0 > div.text-gray-900.hl-text-sm-medium"))
        )
        actions.move_to_element(add_phone_number)
        actions.click()
        actions.perform()  
        
        time.sleep(10)

        # Click Filter to filter phone number 
        filter_phone_number =  driver.find_element(By.CSS_SELECTOR, "#PendoButton\.FILTER > span")        
        filter_phone_number.click()

        # Enter the first three phone number digits to filter with
        number_input  = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#filter > div.n-input-wrapper > div.n-input__input > input"))
        )     
        number_input.send_keys(NUMBER_DIGITS)

        # Select the 'Match to' filter option
        match_option = driver.find_elements(By.XPATH, "//*[@id='select-provider']")

        match_option[1].click()
        option = driver.find_element(By.XPATH, "//div[contains(@class, 'n-base-select-option') and text()='First part of number']")
        option.click()         

        # Click on apply to filter the phone numbers
        apply_button  = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#btn-apply > span > div"))
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
            number = driver.find_element(By.CSS_SELECTOR, "#modal-buy-number-step-1 > div:nth-child(2) > div > div.ghl-table-container > div.n-data-table.n-data-table--bottom-bordered.n-data-table--single-line > div > div > div.n-data-table-base-table-body.n-scrollbar > div.v-vl > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div > div.shrink-1.mr-2.text-gray-900.hl-text-sm-medium")
           
        else:
            raise Exception(f"No phone number found.")  # Raise an exception if no account is found


        # Buy  a number
        buy_number = WebDriverWait(driver, 180).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#btn-move-numbers'))
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
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.binary_location = CHROME_DRIVER_PATH  
    driver = webdriver.Chrome(options=chrome_options)
    # Create ActionChains object
    actions = ActionChains(driver)
    phone = None
    for retry in range(max_retries):
        try:
            phone = buy_phone_number(driver, actions, SUB_ACCOUNT, NUMBER_DIGITS, USER_EMAIL, USER_EMAIL_PASSWORD, EMAIL, EMAIL_PASSWORD)
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
        driver.quit()
        return phone
    

def a2p_ein_business_reg(driver, actions, sub_user):
    print()
    print("On business details page")

    ## Business Details
    classic_inputs  = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")
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
    business_types = driver.find_elements(By.CSS_SELECTOR, "div.n-base-select-option__content")
    for i, bus in enumerate(business_types):
        if sub_user.business_type == bus.text:
            bus.click() 
    print()
    print("Selected business type")


    # Business Registration ID Type (Select field, select the first option)
    driver.find_element(By.ID, "SelectBusinessRegistrationType").click()
    time.sleep(2)
    business_registration_ids = driver.find_elements(By.CSS_SELECTOR, "div.n-base-select-option__content")
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

    scrollable_div = driver.find_elements(By.CSS_SELECTOR, "div.n-scrollbar")[0]

    # Set the initial scroll position and the amount to scroll each time
    scroll_increment = 50  # The amount of pixels to scroll each time
    scroll_position = 0  # Initial scroll position

    # Get the current scrollHeight of the content
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    # Keep scrolling in increments until the bottom is reached
    while scroll_position < scroll_height:
        # Scroll down in the div
        driver.execute_script("arguments[0].scrollTop = arguments[1]", scrollable_div, scroll_position)
        
        # Wait a bit for potentially lazy-loaded content to load
        time.sleep(0.1)
        
        # Update the scroll position and scrollHeight
        scroll_position += scroll_increment
        new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        
        # Check if the scrollHeight has changed due to new content being loaded and update if so
        if new_scroll_height > scroll_height:
            scroll_height = new_scroll_height
        else:
            # If no new content, break the loop as we have likely reached the bottom
            break
        print("\n", scroll_height, scroll_position, new_scroll_height)

    # Get all the loaded options
    business_industries_options = driver.find_elements(By.CSS_SELECTOR, "div.n-base-select-option__content")

    # Search for the desired industry and click it if found
    industry_found = False
    for option in business_industries_options:
        if option.text == sub_user.industry:
            option.click()
            print(f"\nEntered business Engineering: {option.text}")
            industry_found = True
            break

    # If the desired industry is not found, select 'Online'
    if not industry_found:
        for option in business_industries_options:
            if option.text == 'Engineering':
                option.click()
                print("\nIndustry doesn't match, selected Engineering.....")
                break

    # Business Email
    business_email_input = classic_inputs[2]
    business_email_input.click()  # Focus on the input field
    business_email_input.clear()  # Clear the field
    time.sleep(0.5)  # Short delay to allow the field to clear
    business_email_input.send_keys(Keys.BACK_SPACE * 50)  # Ensure the field is cleared by sending backspace
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
    region_labels = [checkbox.find_element(By.CSS_SELECTOR, "span.n-checkbox__label").text for checkbox in region_checkboxes]

    # Business Region of Operations
    # Click the checkboxes based on the sub_user's business region operations
    selected_regions = sub_user.business_region_operation.split(' ')  
    for checkbox, label in zip(region_checkboxes, region_labels):
        # If the label is in sub_user's business regions, or if none are and label is 'USA & Canada', click the checkbox
        if label in selected_regions or (not any(region in selected_regions for region in region_labels) and label == "USA & Canada"):
            checkbox.click()

    print()
    print("Selected business region of operations")

    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.n-button.n-button--primary-type.n-button--medium-type"))
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()  
    print()
    print("Clicked continue ")

    time.sleep(5)


def a2p_ein_business_add(driver, actions, sub_user):

    ## Business Street Address
    
    classic_inputs  = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

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
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.n-button.n-button--primary-type.n-button--medium-type"))
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()  
    print()
    print("Clicked continue ")

    time.sleep(5)


def a2p_ein_business_contact(driver, actions, sub_user):
    ## First Name
    
    classic_inputs  = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")

    first_name = classic_inputs[0]
    first_name.click()
    first_name.clear()
    time.sleep(0.5)
    first_name.send_keys(Keys.BACK_SPACE * 50)
    first_name.send_keys(sub_user.first_name)
    print("\n First Name entered")

    ## Last Name
    last_name = classic_inputs[1]
    last_name.click()
    last_name.clear()
    time.sleep(0.5)
    last_name.send_keys(Keys.BACK_SPACE * 50)
    last_name.send_keys(sub_user.last_name)
    print("\n Last Name entered")

    ## Contact Email
    contact_email = classic_inputs[2]
    contact_email.click()
    contact_email.clear()
    time.sleep(0.5)
    contact_email.send_keys(Keys.BACK_SPACE * 50)
    contact_email.send_keys(sub_user.contact_email)
    print("\n Contact Email entered")


    ## Contact Phone
    contact_phone = classic_inputs[3]
    contact_phone.click()
    contact_phone.clear()
    time.sleep(0.5)
    contact_phone.send_keys(Keys.BACK_SPACE * 50)
    contact_phone.send_keys(sub_user.contact_phone)
    print("\n Contact Phone entered")

    ## Job position
    driver.find_element(By.CSS_SELECTOR, "div#SelectCountry").click()
    driver.find_element(By.CSS_SELECTOR, "div.n-base-selection-input__content").click()

    time.sleep(5)

    job_position  = driver.find_elements(By.CSS_SELECTOR, "input.n-input__input-el")
    print(len(job_position), "boost")
    job_position.click()
    job_position.clear()
    time.sleep(0.5)
    job_position.send_keys(Keys.BACK_SPACE * 50)
    job_position.send_keys(sub_user.job_position)
    print("\n Job position entered")

    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.n-button.n-button--primary-type.n-button--medium-type"))
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()  
    print()
    print("Clicked continue ")

    time.sleep(5)


def a2p_ein_business_use_case(driver, actions):

    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "div.n-checkbox-box__border").click()

    # Continue to the next form
    _continue = WebDriverWait(driver, 180).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.n-button.n-button--primary-type.n-button--medium-type"))
    )
    actions.move_to_element(_continue)
    actions.click()
    actions.perform()  
    print()
    print("Clicked continue ")

    time.sleep(5)

def a2p_register(driver, actions, sub_user, SUB_ACCOUNT, USER_EMAIL, USER_EMAIL_PASSWORD, EMAIL, EMAIL_PASSWORD):
    # Navigate to the login page

    print()
    print("Loading site...")
    driver.get('https://app.thefollowupagency.com/')

    wait = WebDriverWait(driver, 20)

    # Find the username and password input fields and the submit button
    username_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID,"password")
    submit_button = driver.find_element(By.XPATH, '//button[contains(text(), "Sign in")]')

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
        send_code_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Send Security Code")]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
        send_code_button.click()

        time.sleep(10)    # wait for the OTP to be sent

        # Now handle the OTP
        otp_verification(driver, USER_EMAIL, USER_EMAIL_PASSWORD)

        print()
        print("OTP verified successfully")

        print()
        print("Login successful!")

        # Click on switch account to select a sub account
        switch_account = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".hl_location-text .hl_switcher-loc-name"))
        )
        switch_account.click()

        print()
        print("Select account section displayed")
        
        # Wait for the list container to appear
        list_container = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#location-switcher-sidbar-v2 > div.hl_v2-location_switcher"))
        )
 
        # Wait for the list of items to load (adjust the timeout and locator as needed)
        wait = WebDriverWait(driver, 180)
        list_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hl_account")))
        
        # Search for sub account
        search_input = list_container.find_element(By.CSS_SELECTOR, 'input[placeholder="Search for a sub-account"]')
        search_input.send_keys(SUB_ACCOUNT)

        # Wait for filtering of sub accounts        
        time.sleep(5)

        try:
            # Select the first sub account
            wait = WebDriverWait(driver, 180)
            list_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hl_account")))
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
        trust_center_link = ul_element.find_element(By.XPATH, ".//a[contains(text(), ' Trust Center ')]")

        # Move to the Trust Center link and click on it
        actions.move_to_element(trust_center_link)
        actions.click()
        actions.perform()

        print()
        print("Loading Trust Center page....")


        # Select Phone Numbers form the settings options
        start_registration = WebDriverWait(driver, 180).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button#button-action-0"))
        )
        actions.move_to_element(start_registration)
        actions.click()
        actions.perform()  
        print()
        print("Starting registration")


        # check the radio button for registered EIN
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input.n-radio-input")
        if len(radio_buttons) > 0 and sub_user.has_ein is True:
            radio_buttons[2].click()
            print()
            print("Selected ein radio button")

            # Continue to the next form
            _continue = WebDriverWait(driver, 180).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button.n-button.n-button--primary-type.n-button--medium-type"))
            )
            actions.move_to_element(_continue)
            actions.click()
            actions.perform()  
            print()
            print("clicked continue")

            # business details registration
            a2p_ein_business_reg(driver, actions, sub_user)

            # business address registration
            a2p_ein_business_add(driver, actions, sub_user)

            # business contact info
            a2p_ein_business_contact(driver, actions, sub_user)

            # business use case
            a2p_ein_business_use_case(driver, actions)

            time.sleep(10)


    except Exception as e:
        print()
        print(f"Operation failed. Error: {e}")


def a2pregister_with_retries(sub_user, max_retries=1):
    # CHROME_DRIVER_PATH = "path/to/chromedriver"

    SUB_ACCOUNT = sub_user.business_name

    # For getting the OTP from emails
    USER_EMAIL = settings.USER_EMAIL
    USER_EMAIL_PASSWORD = settings.USER_EMAIL_PASSWORD

    # For logining into FollowUpAgency
    EMAIL = settings.EMAIL
    EMAIL_PASSWORD = settings.EMAIL_PASSWORD

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('start-maximized')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.binary_location = CHROME_DRIVER_PATH  
    driver = webdriver.Chrome(options=chrome_options)
    # Create ActionChains object
    actions = ActionChains(driver)
    for retry in range(max_retries):
        try:
            a2p_register(driver, actions, sub_user, SUB_ACCOUNT, USER_EMAIL, USER_EMAIL_PASSWORD, EMAIL, EMAIL_PASSWORD)
        except Exception as e:
            print()
            print(f"Operation failed with exception: {e}")
            if retry < max_retries - 1:
                print()
                print("Retrying...")
                time.sleep(5)
            else:
                raise Exception(f"Maximum retries reached")


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
    if phone_number.startswith('+1'):
        phone_number = phone_number[2:]
    
    # Extracting the area code
    area_code = re.search(r'\d{3}', phone_number)
    if area_code:
        return area_code.group()
    else:
        return None