from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim


# https://pypi.python.org/pypi/geopy

def get_location_by_coordinate(latitude, longitude):
    geo_locator = Nominatim()
    location = None
    try:
        location = geo_locator.reverse(str(latitude)+ ', ' + str(longitude), timeout=10)
    except GeocoderTimedOut as e:
        print("Error: geocode failed with latitude:", latitude, ", longitude:", longitude, e.msg)
    if not location:
        return ''
    else:
        return location.address
