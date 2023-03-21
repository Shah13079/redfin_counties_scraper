
import re
from geopy.geocoders import Nominatim
from urllib.parse import urlencode
import numpy
from datetime import datetime
import json
import pytz
import csv
import os
from datetime import date
from random import randint

request_headers = {
    "authority": "www.redfin.com",
    "method": "GET",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
              (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
}


def get_location_api_url(address):
    """Generate latitude and longitude bounds for a given address.
    Args:
        addresses (dictionary): containing address e.g county, state, etc
    Returns:
        str: resulting url to call for route address
    """
    # Initialize Nominatim API
    geolocator = Nominatim(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                  (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        timeout=10)

    county = address["county"]
    state = address["state"]

    location = geolocator.geocode(
        f"{county}, {state}")

    params = {
        "location": "%s %s" % (county, state),
        "start": "0",
        "count": "10",
        "v": "2",
        "market": "false",
        "iss": "false",
        "ooa": "true",
        "mrs": "false",
        "region_id": "NaN",
        "region_type": "NaN",
        "lat": "%s" % location.latitude,
        "lng": "%s" % location.longitude,
    }

    final_url = (
        "https://www.redfin.com/stingray/do/location-autocomplete?"
        + urlencode(params)
    )

    return final_url


def apply_filter(route_url, filter_arg):
    """This function applies suitable filter to a route url to make absolute url.

    Args:
        route_url (string):  route_url generated from get_location_api_url function
        filter_arg (_type_): filter recived from user

    Returns:
        absolute_url
    """
    if isinstance(filter_arg, float):
        url = ("https://www.redfin.com"
               + f"{route_url}/filter/property-type=land")
        return url

    elif 'yr' in filter_arg or 'mo' in filter_arg:
        filter_value = "".join(filter(str.isdigit, filter_arg))
        filter_string = "".join(filter(str.isalpha, filter_arg))
        url = ("https://www.redfin.com"
               + f"{route_url}/filter/property-type=land"
               + f",include=sold-{filter_value}{filter_string}")
        return url


FIELDS_MAP = {
    "XPATH": {

        "Status": '//span[text()="Status"]/following-sibling::span//text()',
        "County": '//span[text()="County"]/following-sibling::div[@class="table-value"]/text()',
        # "State": "",
        "City": '//div[@class="dp-subtext"]/text()',
        "Address": '//div[@class="street-address font-weight-bold"]/text()',
        # "Zip": "",
        "Google Map": '//div[@class="static-map v2"]/img/@src',
        # "Latitutde": "",
        # "Longitude": "",
        "APN": '//span[text()="APN"]/following-sibling::div[@class="table-value"]/text()',
        "Lot Size": '//span[text()="Lot Size"]/following-sibling::span/text()',
        "Price": '(//div[@class="statsValue"]//text())[1]',
        "Community": '//span[text()="Community"]/following-sibling::span/text()',
        "Description": '//div[@class="house-info-container"]',
        # "Sold Date": "",
        # "Days On Market": "",
        "HOA Dues": '//span[text()="HOA Dues"]/following-sibling::span/text()',
        "Sale Type": '//div[@class="property-history-content-container"]//div[contains(text(), "Sold")][1]/text()',
        "Sales History": '//script[contains(text(),"root.__reactServerState")]/text()',
        # "Link": ""
    },

    "REGEX": {


    }
}


def parse_address(address):
    # Define regular expression pattern
    pattern = r'^(.+?),\s*([\w\s]+),\s*([A-Z]{2})\s*(\d{5})$'

    # Apply pattern to address string
    match = re.match(pattern, address)
    if match:
        street_address = (match.group(1) or "")
        city = match.group(2)
        state = match.group(3)
        zip_code = (match.group(4) or "")
        return (street_address, city, state, zip_code)
    else:
        return None


def extract_lat_long_from_url(url):
    """
    Extracts the latitude and longitude values from a Google Maps URL.

    Args:
        url (str): The Google Maps URL containing the latitude and longitude values.

    Returns:
        A tuple containing the latitude and longitude values as floats,
        or "" if the values were not found in the URL.
    """
    try:
        match = re.search(r"center=([\d\.-]+)%2C([\d\.-]+)", url)
    except TypeError:
        return ("", "")
    else:
        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            return (latitude, longitude)
        else:
            return ("", "")


def extract_address_info(original_list):
    """
    Extracts City name, State code, and Zipcode from the given list dynamically.

    Args:
        new_list (list): A list containing City name, State code, and Zipcode.

    Returns:
        tuple: A tuple containing the extracted City name, State code, and Zipcode.

    Example:
        new_list = ['Golden Valley', 'AZ', '86413']
        city, state, zipcode = extract_address_info(new_list)
        # city = 'Golden Valley', state = 'AZ', zipcode = '86413'
    """

    # Initializing variables with default values
    city = ""
    state = ""
    zipcode = "0"

    new_list = [item for item in original_list if item.strip()
                not in (',', '')]

    # Checking length of new_list to determine which fields are present
    if len(new_list) == 3:
        city = new_list[0]
        state = new_list[1]
        zipcode = new_list[2]

    elif len(new_list) == 1:
        city = ''
        state = new_list[0]
        zipcode = ''

    # Returning the extracted values as a tuple
    return (city, state, zipcode)


def sqft_to_acres(area):
    """Converts square feet to acres."""
    if isinstance(area, str):
        area = area.replace(",", "").lower()
        if "sq. ft" in area:
            area = float(area.split(" ")[0])
        elif "acres" in area or "acre" in area:
            return float(area.split(" ")[0])

    try:
        return round(area / 43560, 2)
    except TypeError:
        return ""


def dollar_to_number(dollar_string):
    """Converts $ price to clean numbers."""
    if (dollar_string is None
        or dollar_string == ""
            or dollar_string == "—"):
        return ""
    return float("".join(filter(str.isdigit, dollar_string)))


def convert_timestamp_to_date(timestamp: int, timezone: str = 'US/Eastern') -> str:
    """
    Convert a Unix timestamp (in milliseconds) to a string representing the date in "Jan 12, 2023" format.

    Args:
        timestamp (int): The Unix timestamp (in milliseconds) to convert.
        timezone (str, optional): The timezone to use for the conversion. Defaults to 'US/Eastern'.

    Returns:
        str: A string representing the date in "Jan 12, 2023" format.
    """
    # Convert timestamp to datetime object in UTC timezone
    datetime_obj = datetime.utcfromtimestamp(
        timestamp / 1000.0).replace(tzinfo=pytz.UTC)

    # Convert datetime object to specified timezone
    timezone_obj = pytz.timezone(timezone)
    datetime_obj = datetime_obj.astimezone(timezone_obj)

    # Format datetime object as string in "Jan 12, 2023" format
    date_string = datetime_obj.strftime('%b %d, %Y')

    # Return date string
    return date_string


def remove_parenthesis(status):
    """
    This function takes a string as input and removes any parentheses and their contents
    from the string, returning the modified string.

    Parameters:
        status (str): The input string to modify.

    Returns:
        str: The modified string with parentheses and their contents removed.

    Example:
        >>> string = "Sold (congintent)"
        >>> remove_parenthesis(string)
        'Sold'
    """
    if "(" in status:
        return status.split("(")[0].strip()
    return status

# Y


def parse_sales_history(sales_history):
    """parsing sales history from hidden raw source availble for each listing.

    Args:
        sales_history (string): extracting from listing avaible in
        "root.__reactServerState" hidden script.

    Returns:
        dictionary: parse sales history return JSON dictionary
        contains of date, event description, and price.

    """
    date = ''
    price = ''
    events_list = []

    g = sales_history.split(
        "propertyHistoryInfo")[-1].split(',\\"mediaBrowserInfoBySourceId\\')[0].split('"events\\')[-1].strip('":')
    final_list = g.replace("\\", "")

    json_response = json.loads(final_list)
    for each_event in json_response:
        date = each_event['eventDate']
        try:
            price = each_event['price']
        except:
            price = '     '
        event_description = each_event['eventDescription']
        date = convert_timestamp_to_date(date)

        my_data = {
            "Date": date,
            "Status": event_description,
            "Price": price
        }
        events_list.append(my_data)
    return json.dumps(events_list)


def sales_type(final_sales_history):
    """Find sales type based on the sales history."""
    sold_sales = [
        sale for sale in final_sales_history if remove_parenthesis(sale["Status"]) == "Sold"]

    sorted_by_date_history = sorted(sold_sales, key=lambda x: datetime.strptime(
        x['Date'], '%b %d, %Y'), reverse=True)
    if len(sorted_by_date_history) >= 2:
        if sorted_by_date_history[0]['Date'] == sorted_by_date_history[1]['Date']:
            if (extract_string_in_parentheses(sorted_by_date_history[0]['Status']) == 'Public Records' and extract_string_in_parentheses(sorted_by_date_history[1]['Status']) == 'MLS') or (extract_string_in_parentheses(sorted_by_date_history[0]['Status']) == 'MLS' and extract_string_in_parentheses(sorted_by_date_history[1]['Status']) == 'Public Records'):
                return 'MLS'
    return extract_string_in_parentheses(sorted_by_date_history[0]['Status'])


def calculate_days_on_market(sales_history):
    """Calculate the number of days that a property was on the market based on its sales history.

    Args:
        sales_history (list): A list of dictionaries representing the sales history of the property. Each dictionary
        contains the following keys: "Date" (string), "Status" (string), and "Price" (string or integer).

    Returns:
        A tuple containing the most recent sold date (string in the format "MM/DD/YYYY"),
        and the number of days between those dates (integer).
    """
    sales_history = json.loads(sales_history)

    # Find sales type
    get_sales_type = sales_type(sales_history)

    # Extract the most recent listed and most recent sold dates
    listed_sales = [remove_parenthesis(
        sale) for sale in sales_history if remove_parenthesis(sale["Status"]) == "Listed"]

    sold_sales = [remove_parenthesis(
        sale) for sale in sales_history if remove_parenthesis(sale["Status"]) == "Sold"]

    most_recent_sold_sale = max(
        sold_sales, key=lambda x: datetime.strptime(x["Date"], "%b %d, %Y"))
    try:
        most_recent_listed_sale = max(
            listed_sales, key=lambda x: datetime.strptime(x["Date"], "%b %d, %Y"))
    except ValueError:
        days_between_dates = 0
    else:
        # Calculate the days on market
        days_between_dates = (datetime.strptime(
            most_recent_sold_sale["Date"], "%b %d, %Y") - datetime.strptime(most_recent_listed_sale["Date"], "%b %d, %Y")).days

    # Format the dates as "MM/DD/YYYY"
    most_recent_sold_date = datetime.strptime(
        most_recent_sold_sale["Date"], "%b %d, %Y").strftime("%m/%d/%Y")

    return (most_recent_sold_date, days_between_dates, get_sales_type)


def extract_string_in_parentheses(input_string):
    """Extracts the string between the first pair of parentheses in the input string.

    Args:
        input_string (str): The input string containing the parentheses.

    Returns:
        str: The string between the first pair of parentheses, or an empty string if no parentheses are found.
    """
    match = re.search(r'\((.*?)\)', input_string)
    if match:
        return match.group(1)
    else:
        return ""


def append_dict_to_csv_file(file_prefix, dict_data):
    """
    Append a dictionary of data to a CSV file, creating the file if it doesn't exist.

    Parameters:
        file_prefix (str): The prefix to use for the CSV file name.
        dict_data (dict): A dictionary containing the row data to append to the CSV file.

    Returns:
        None
    """

    # Get the current date as a string in the "YYYY-MM-DD" format
    file_date = date.today().strftime("%Y-%m-%d")

    # Construct the full file path using the file prefix and date string
    file_path = f"{file_prefix}_{file_date}.csv"

    # Check if the file already exists
    file_exists = os.path.isfile(file_path)

    # Open the CSV file in append mode
    with open(file_path, mode='a', newline='', encoding="utf-8") as csv_file:
        # Get the field names from the dictionary
        fieldnames = dict_data.keys()

        # Create a DictWriter object using the field names and the CSV file
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # If the file doesn't exist, write the header row
        if not file_exists:
            writer.writeheader()

        # Write the row data to the CSV file
        writer.writerow(dict_data)
