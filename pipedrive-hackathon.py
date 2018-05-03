from flask import Flask
import sys
import requests
from flask import jsonify
app = Flask(__name__)

def dealToMyObject(deal):
  dealDict = {"name" : deal["title"],
              "value" : deal["value"],
              "id" : deal["id"],
              "probability": deal["probability"],
               "address" : deal["cb2d2fbdecb036750c820899ffe8f7c63861c777_formatted_address"]}
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

if __name__ == '__main__':
    app.config['company_domain'] = sys.argv[1]
    app.config['api_token'] = sys.argv[2]
    app.run()
