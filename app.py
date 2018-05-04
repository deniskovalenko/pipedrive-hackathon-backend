from flask import Flask
from flask import request
from flask import jsonify
import sys
import requests
app = Flask(__name__)

def getCoordinates(address):
    return requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=" + app.config.get('google_maps_api_key')).json()

def dealToMyObject(deal):
  address = deal["cb2d2fbdecb036750c820899ffe8f7c63861c777_formatted_address"]
  coordinates = {'lat' : 59, 'lng' : 32}
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
    url = "https://" + app.config.get('company_domain') + ".pipedrive.com/v1/deals?api_token=" + app.config.get('api_token')
    result = requests.get(url)
    dealsList = result.json()["data"]
    clearedDealsList = preprocessDeals(dealsList)
    return clearedDealsList

@app.route('/')
def build_path():
    return "Hello, Salesman helper. To get to more useful page please use \n GET /deals \n or \n POST /deals/route [1,3,6,9] (supply array of deals' IDs in array"

@app.route('/deals')
def deals():
    deals = getPipeDriveDeals()
    return jsonify(deals)

@app.route('/deals/route', methods=['POST'])
def routes():
    ids = request.get_json()
    deals = getPipeDriveDeals()
    dealsSelected = list(filter(lambda x: x["id"] in ids, deals))
    # todo build matrxi
    return jsonify(dealsSelected)


if __name__ == '__main__':
    app.config['company_domain'] = sys.argv[1]
    app.config['api_token'] = sys.argv[2]
    app.config['google_maps_api_key'] = sys.argv[3]
    app.run(host='0.0.0.0',port='8080')
