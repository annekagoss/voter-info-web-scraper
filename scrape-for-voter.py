import re
import time
import asyncio

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

LAST_NAME = 'Goss'
FIRST_NAME = 'Anneka'
DOB = '10/23/1988'
COUNTY = 'Queens'
ZIP_CODE = '11104'
HOUSE_NUMBER = '47-08'
STREET_NAME = '39th ave'

class Voter:
    def __init__(self):
        self.input = {}
        self.election_day_site = {}
        self.early_voting_site = {}

voter = Voter()

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options) # diver

async def request_user_input():
    first_name = ''
    last_name = ''
    dob = ''
    county = ''
    zip_code = ''
    house_number = ''
    street_name = ''

    while not first_name:
        first_name = input("Enter your first name: ")
    voter.input['first_name'] = first_name
    
    while not last_name:
        last_name = input("Enter your last name: ")
    voter.input['last_name'] = last_name

    while not dob:
        dob = input("Enter your DOB (MM/DD/YYYY): ")
    voter.input['dob'] = dob

    while not county:
        county = input("Enter your county: ")
    voter.input['county'] = county.capitalize()

    while not zip_code:
        zip_code = input("Enter your zip code: ")
    voter.input['zip_code'] = zip_code

    while not house_number:
        house_number = input("Enter your house number: ")
    voter.input['house_number'] = house_number

    while not street_name:
        street_name = input("Enter your street name: ")
    voter.input['street_name'] = street_name

async def get_ny_voter_data(voter):
    print('\nFinding voter information...\n')

    URL = 'https://voterlookup.elections.ny.gov'

    driver.get(URL)

    county_select = Select(driver.find_element_by_name('SelectedCountyId'))
    county_select.select_by_visible_text(voter.input['county'])

    last_name_input = driver.find_element_by_name('Lastname')
    last_name_input.send_keys(voter.input['last_name'])

    first_name_input = driver.find_element_by_name('Firstname')
    first_name_input.send_keys(voter.input['first_name'])

    date_of_birth_input = driver.find_element_by_id('dob')
    date_of_birth_input.send_keys(voter.input['dob'])

    zip_code_input = driver.find_element_by_name('Zipcode')
    zip_code_input.send_keys(voter.input['zip_code'])

    submit_button = driver.find_element_by_id('submitbtn')
    submit_button.click()

    # Verify information
    time.sleep(2)
    submit_button = driver.find_element_by_id('submitbtn')
    driver.execute_script("arguments[0].click();", submit_button)

    #Results
    time.sleep(2)

    voter_information_items = driver.find_elements_by_xpath("//div[contains(@class, 'InfoBoxBody')]/div/div")

    for element in voter_information_items:
        if ("Name") in element.text: 
            voter.name = element.text.split("Name :")[1].strip()
        elif ("Political Party") in element.text: 
            voter.political_party = element.text.split("Political Party :")[1].strip()
        elif ("Mailing Address") in element.text:
            voter.mailing_address = element.text.split("Mailing Address (if any) :")[1].strip()
        elif ("Address") in element.text: 
            voter.address = element.text.split("Address :")[1].strip()
        elif ("Voter Status") in element.text:
            voter.voter_status = element.text.split("Voter Status :")[1].strip()
        elif ("Election District") in element.text:
            voter.election_district = element.text.split("Election District :")[1].strip()
        elif ("County Legislative District") in element.text:
            voter.county_legislative_district = element.text.split("County Legislative District :")[1].strip()
        elif ("Senate District") in element.text:
            voter.senate_district = element.text.split("Senate District :")[1].strip()
        elif ("Assembly District") in element.text:
            voter.assembly_district = element.text.split("Assembly District :")[1].strip()
        elif ("Congressional District") in element.text:
            voter.congressional_district = element.text.split("Congressional District :")[1].strip()
        elif ("Town") in element.text:
            voter.town = element.text.split("Town :")[1].strip()
        elif ("Ward") in element.text:
            voter.ward = element.text.split("Ward :")[1].strip()

    print('\n')
    print('Voter Information')
    print('--------------------------------------------------')
    attrs = vars(voter)
    print(''.join("%s: %s\n" % item for item in attrs.items()))

    return True

async def get_ny_poll_sites(voter):
    print('\nFinding voter poll locations...\n')

    URL = 'https://nyc.pollsitelocator.com/search'
    driver.get(URL)

    house_number_input = driver.find_element_by_name('txtHouseNumber')
    house_number_input.send_keys(voter.input['house_number'])

    street_name_input = driver.find_element_by_name('txtStreetName')
    street_name_input.send_keys(voter.input['street_name'])

    zip_code_input = driver.find_element_by_name('txtZipCode')
    zip_code_input.send_keys(voter.input['zip_code'])

    submit_button = driver.find_element_by_id('btnSearch')
    driver.execute_script("arguments[0].click();", submit_button)

    #Results
    time.sleep(2)

    info_path = "/div[contains(@class, 'ps-info-wrapper')]/div[contains(@class, 'ps-info')]/div[contains(@class, 'basic-info-container')]/div[contains(@class, 'basic-info')]"
    details_path = "/div[contains(@class, 'ps-info-wrapper')]/table[contains(@class, 'expando-details')]/tbody"
    hour_rows_path = "/table[contains(@class, 'group-list')]/tbody/tr"

    election_day_group = "//li[contains(@class, 'group-electionday')]"
    early_voting_group = "//li[contains(@class, 'group-early')]"
    election_day_info = election_day_group + info_path
    early_voting_info =  early_voting_group + info_path
    election_day_details = election_day_group + details_path
    early_voting_details = early_voting_group + details_path

    voter.election_day_site['name'] = driver.find_element_by_xpath(election_day_info + "/h1[contains(@class, 'site-name')]").text
    voter.election_day_site['address'] = driver.find_element_by_xpath(election_day_info + "/h2[contains(@class, 'site-address')]").text
    voter.election_day_site['entrance'] = driver.find_element_by_xpath(election_day_details + "/tr[contains(@class, 'voter-entrance')]/td[contains(@class, 'expando-val')]").text
    voter.election_day_site['accessible-entrance'] = driver.find_element_by_xpath(election_day_details + "/tr[contains(@class, 'accessible-entrance')]/td[contains(@class, 'expando-val')]").text

    election_day_hour_rows = driver.find_elements_by_xpath(election_day_group + hour_rows_path)
    voter.election_day_site['hours'] = []
    for hour_row in election_day_hour_rows:
        voter.election_day_site['hours'].append(hour_row.text)

    voter.early_voting_site['name'] = driver.find_element_by_xpath(early_voting_info + "/h1[contains(@class, 'site-name')]").text
    voter.early_voting_site['address'] = driver.find_element_by_xpath(early_voting_info + "/h2[contains(@class, 'site-address')]").text
    voter.early_voting_site['entrance'] = driver.find_element_by_xpath(early_voting_details + "/tr[contains(@class, 'voter-entrance')]/td[contains(@class, 'expando-val')]").text
    voter.early_voting_site['accessible-entrance'] = driver.find_element_by_xpath(early_voting_details + "/tr[contains(@class, 'accessible-entrance')]/td[contains(@class, 'expando-val')]").text

    early_voting_hour_rows = driver.find_elements_by_xpath(early_voting_group + hour_rows_path)
    voter.early_voting_site['hours'] = []
    for hour_row in early_voting_hour_rows:
        voter.early_voting_site['hours'].append(hour_row.text)

    print('Election Day Location')
    print('--------------------------------------------------')
    print(''.join("%s: %s\n" % item for item in vars(voter)['election_day_site'].items()))

    print('Early Voting Location')
    print('--------------------------------------------------')
    print(''.join("%s: %s\n" % item for item in vars(voter)['early_voting_site'].items()))

    return True

async def scrape_data():
    async_request_user_input = asyncio.create_task(request_user_input())
    async_get_ny_voter_data = asyncio.create_task(get_ny_voter_data(voter))
    async_get_ny_poll_sites = asyncio.create_task(get_ny_poll_sites(voter))

    await async_request_user_input
    await async_get_ny_voter_data
    await async_get_ny_poll_sites
    driver.quit()

asyncio.run(scrape_data())


