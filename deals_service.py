import requests

from deal_list_sorter import DealListSorter


class DealsService(object):

    def __init__(self, config):
        self.config = config
        self.sorter = DealListSorter()
    # in memoru non-thread-safe cache for routes and pipedrive deals
    cache = {}

    def getCoordinates(self, address):
        return requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=" + self.config.get(
                'google_maps_api_key')).json()

    def getRouteFromGoogleApi(self, currentAddress, deals):
        # todo construct actual URL
        url = "https://maps.googleapis.com/maps/api/directions/json?origin=Raekoja%20plats%2C2%2CTartu&destination=Raekoja%20plats%2C2%2CTartu&waypoints=optimize%3Atrue%7CTuru%202%2C%2051013%20Tartu%2C%20Estonia%2C&api_key=" + self.config.get(
            'google_maps_api_key')
        response = None
        if (url in self.cache.keys()):
            response = self.cache[url]
            print("returning route from cache")
        else:
            response = requests.get(url)
            self.cache[url] = response
        return response.json()

    def dealToMyObject(self,deal):
        address = deal["cb2d2fbdecb036750c820899ffe8f7c63861c777_formatted_address"]
        # in case we have deal without address just show something near Tartu
        coordinates = {'lat': 58.39, 'lng': 26.74}
        if (address != None):
            coordinates = self.getCoordinates(address)["results"][0]["geometry"]["location"]

        dealDict = {"name": deal["title"],
                    "coordinates": coordinates,
                    "value": deal["value"],
                    "id": deal["id"],
                    "probability": deal["probability"],
                    "address": address}
        return dealDict

    def preprocessDeals(self,deals):
        return list(map(lambda deal: self.dealToMyObject(deal), deals))

    def getPipeDriveDeals(self):
        clearedDealsList = None
        if "pipedriveDeals" in self.cache.keys():
            clearedDealsList = self.cache["pipedriveDeals"]
        else:
            url = "https://" + self.config.get('company_domain') + ".pipedrive.com/v1/deals?api_token=" + self.config.get(
                'api_token')
            result = requests.get(url)
            dealsList = result.json()["data"]
            list = self.preprocessDeals(dealsList)
            # todo sort by value*probability
            clearedDealsList = self.sorter.sort_deals(list)
            self.cache["pipedriveDeals"] = clearedDealsList
        return clearedDealsList
