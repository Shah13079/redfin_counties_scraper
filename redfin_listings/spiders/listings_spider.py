import json
import scrapy
import pandas as pd
from ..utility import *
from w3lib.html import remove_tags
from scrapy_selenium import SeleniumRequest


class ListingsSpiderSpider(scrapy.Spider):
    name = "listings"
    allowed_domains = ["www.redfin.com"]

    def start_requests(self):
        """This function is called when the spider is started."""
        try:
            df = pd.read_csv(r"RedFinListingCounties.csv")
        except FileNotFoundError as e:
            print("File not found, please check the path to input file: %s" % e)
        else:
            for index, row in df.iterrows():
                county = row["County"]
                state = row["State"]
                filter = row["Filter"]

                # Calling function to get location-autocomplete API URL
                autosuggest_api_url = get_location_api_url(
                    {"state": state, "county": county}
                )

                yield scrapy.Request(
                    url=autosuggest_api_url,
                    callback=self.parse_route_url,
                    headers=request_headers,
                    dont_filter=True,
                    meta={"state": state, "county": county, "filter": filter},
                )

    def parse_route_url(self, response):
        """This function is called when a request is made to location auto seggest  API\
            It parse route url.
        Args:
            response (scrapy.http.response.Response): response object
        """
        state = response.meta["state"]
        county = response.meta["county"]
        filter = response.meta["filter"]

        json_response = json.loads(response.text.replace("{}&&", ""))
        rows = json_response["payload"].get("sections")[0].get("rows")
        for each in rows:
            name = each.get("name")
            route_url = each.get("url")

            if (
                f"/{state}" in route_url
                and "/%s" % (county.replace(" ", "-")) in route_url
                    and name == county):
                # Call apply_filter function to apply filter
                absolute_url = apply_filter(route_url, filter)

                yield SeleniumRequest(
                    url=absolute_url,
                    callback=self.parse_pages,
                    meta={"state": state, "county": county,
                          "filter": filter, "page_num": 1}
                )

    def parse_pages(self, response):
        # Iterate through each listings
        state = response.meta["state"]
        county = response.meta["county"]
        filter = response.meta["filter"]
        page_num = response.meta["page_num"]

        listings = response.xpath(
            '//div[@class="HomeCardContainer defaultSplitMapListView"]//a')
        for each_property in listings:
            yield scrapy.Request(
                url=response.urljoin(each_property.xpath(".//@href").get()),
                callback=self.parse_listing,
                meta={"state": state, "county": county, "filter": filter},
                headers=request_headers,
                dont_filter=False,

            )

        # Checking if next page is available,
        next_page = response.xpath(
            '//span[@class="pageText"]/text()').get()
        if next_page:
            total_pages = next_page.split("of")[1].strip()

            if page_num < int(total_pages):
                page_num += 1
                next_url = response.url.split(
                    "/page")[0]+"/page-%s" % (page_num) if"/page" in response.url else response.url+"/page-%s" % (page_num)
                yield SeleniumRequest(
                    url=next_url,
                    callback=self.parse_pages,
                    meta={"state": state, "county": county,
                          "filter": filter, "page_num": page_num},
                )

    def parse_listing(self, response):
        sales_history = ''
        sold_date = ''
        days_on_market = ''
        sale_type = ''

        filter = response.meta["filter"]
        # If properties are for sale not sold ones, then assign pre-define values to vars
        if isinstance(filter, float):
            sale_type = "For Sale"
            days_on_market = 0

        XPATH = FIELDS_MAP["XPATH"]
        status = response.xpath(XPATH["Status"]).get()
        lot_size = sqft_to_acres(response.xpath(XPATH["Lot Size"]).get())
        hoa_dues = (dollar_to_number(
            response.xpath(XPATH["HOA Dues"]).get()) or 0)
        community = response.xpath(XPATH["Community"]).get() or ""
        county = response.xpath(XPATH["County"]).get()
        apn = response.xpath(XPATH["APN"]).get()
        apn = '' if apn == '—' else apn
        price = dollar_to_number(response.xpath(XPATH["Price"]).get())
        Description = remove_tags(
            (response.xpath(XPATH["Description"]).get() or "")).replace("Continue reading", '')
        street_address = response.xpath(XPATH["Address"]).get()
        city_state_zip = extract_address_info(
            response.xpath(XPATH["City"]).getall())

        if "Unknown Address" in street_address:
            street_address = ""

        city = city_state_zip[0]
        state = city_state_zip[1]
        zip_code = city_state_zip[2]

        gmap_url = extract_lat_long_from_url(
            response.xpath(XPATH["Google Map"]).get())
        latitude, longitude = gmap_url[0], gmap_url[1]
        listing_url = response.url
        if not isinstance(filter, float):
            sales_history = response.xpath(XPATH["Sales History"]).get()
            if sales_history:
                sales_history = parse_sales_history(sales_history)
            sold_date_ = calculate_days_on_market(sales_history)
            sold_date = sold_date_[0]
            days_on_market = sold_date_[1]
            sale_type = sold_date_[2]

        fields_dic = {
            "Status": status,
            "County": county,
            "State": state,
            "City": city,
            "Address": street_address,
            "Zip": zip_code,
            "latitude": latitude,
            "longitude": longitude,
            "APN": apn,
            "Lot size": lot_size,
            "Price": price,
            "Community": community,
            "Description": Description,
            "Sold date": sold_date,
            "Days on market": days_on_market,
            "HOA Dues": hoa_dues,
            "Sale Type": sale_type,
            "Sales History": sales_history,
            "Url": listing_url
        }

        yield fields_dic

        append_dict_to_csv_file("redfin_listings", fields_dic)
        print(fields_dic, end="\n\n")
