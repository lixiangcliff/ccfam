from geopy.geocoders import Nominatim


# https://pypi.python.org/pypi/geopy

def get_location_by_coordinate(latitude, longitude):
    geo_locator = Nominatim()
    location = geo_locator.reverse(str(latitude)+ ', ' + str(longitude))
    return location.address
