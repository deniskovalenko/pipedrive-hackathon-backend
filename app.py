from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import sys

from deals_service import DealsService

app = Flask(__name__)
CORS(app)
deals_service = DealsService(app.config)

@app.route('/')
def build_path():
    return "Hello, Salesman helper. To get to more useful page please use \n GET /deals \n or \n POST /deals/route {currentAddress : 'Turu 2, Tartu, Estonia', idsForDeals : [1,3,6,9]} (supply array of deals' IDs in array and curreny address"

@app.route('/deals')
def deals():
    deals = deals_service.getPipeDriveDeals()
    return jsonify(deals)


@app.route('/deals/route', methods=['POST'])
def routes():
    addressWithDealIDs = request.get_json()
    currentAddress = addressWithDealIDs["currentAddress"]
    ids = addressWithDealIDs["idsForDeals"]
    # todo don't query again, store it as "global state"
    deals = deals_service.getPipeDriveDeals()
    dealsSelected = list(filter(lambda x: x["id"] in ids, deals))
    routeInfo = deals_service.getRouteFromGoogleApi(currentAddress, dealsSelected)
    return jsonify(routeInfo)

if __name__ == '__main__':
    app.config['company_domain'] = sys.argv[1]
    app.config['api_token'] = sys.argv[2]
    app.config['google_maps_api_key'] = sys.argv[3]
    app.run(host='0.0.0.0',port=8080)
