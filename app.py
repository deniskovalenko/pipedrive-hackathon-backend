from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import sys
import requests
app = Flask(__name__)
CORS(app)

#in memoru non-thread-safe cache for routes and pipedrive deals
cache = {}

def getCoordinates(address):
    return requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=" + app.config.get('google_maps_api_key')).json()

def getRouteFromGoogleApi(currentAddress, deals):
    #todo construct actual URL
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=Raekoja%20plats%2C2%2CTartu&destination=Raekoja%20plats%2C2%2CTartu&waypoints=optimize%3Atrue%7CTuru%202%2C%2051013%20Tartu%2C%20Estonia%2C&api_key=" + app.config.get('google_maps_api_key')
    response = None
    if (url in cache.keys()) :
        response = cache[url]
        print("returning route from cache")
    else:
        response = requests.get(url)
        cache[url] = response
    return response.json()

def dealToMyObject(deal):
  address = deal["cb2d2fbdecb036750c820899ffe8f7c63861c777_formatted_address"]
  #in case we have deal without address just show something near Tartu
  coordinates = {'lat' : 58.39, 'lng' : 26.74}
  if (address!= None):
      coordinates = getCoordinates(address)["results"][0]["geometry"]["location"]

  dealDict = {"name" : deal["title"],
              "coordinates" : coordinates,
              "value" : deal["value"],
              "id" : deal["id"],
              "probability": deal["probability"],
               "address" : address}
  return dealDict

def preprocessDeals(deals):
   return list(map(lambda deal : dealToMyObject(deal), deals))

def getPipeDriveDeals():
    clearedDealsList = None
    if "pipedriveDeals" in cache.keys():
        clearedDealsList = cache["pipedriveDeals"]
    else:
        url = "https://" + app.config.get('company_domain') + ".pipedrive.com/v1/deals?api_token=" + app.config.get(
            'api_token')
        result = requests.get(url)
        dealsList = result.json()["data"]
        clearedDealsList = preprocessDeals(dealsList)
        # todo sort by value*probability
        cache["pipedriveDeals"] = clearedDealsList
    return clearedDealsList

@app.route('/')
def build_path():
    return "Hello, Salesman helper. To get to more useful page please use \n GET /deals \n or \n POST /deals/route {currentAddress : 'Turu 2, Tartu, Estonia', idsForDeals : [1,3,6,9]} (supply array of deals' IDs in array and curreny address"

@app.route('/deals')
def deals():
    deals = getPipeDriveDeals()
    return jsonify(deals)


@app.route('/deals/route', methods=['POST'])
def routes():
    addressWithDealIDs = request.get_json()
    currentAddress = addressWithDealIDs["currentAddress"]
    ids = addressWithDealIDs["idsForDeals"]
    # todo don't query again, store it as "global state"
    deals = getPipeDriveDeals()
    dealsSelected = list(filter(lambda x: x["id"] in ids, deals))
    routeInfo = getRouteFromGoogleApi(currentAddress, dealsSelected)
    return jsonify(routeInfo)

if __name__ == '__main__':
    app.config['company_domain'] = sys.argv[1]
    app.config['api_token'] = sys.argv[2]
    app.config['google_maps_api_key'] = sys.argv[3]
    app.run(host='0.0.0.0',port=8080)
