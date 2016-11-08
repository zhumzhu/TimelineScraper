import logging,string,random
import os,json
from flask import Flask, request, jsonify, Response
from functools import wraps

from timelinescraper.TimelineScraper import TimelineScraper

from timelinescraper.engines.TradingPlatformsTsEngine import TradingPlatformsTradesTsEngine, TradingPlatformsOrderbookTsEngine
from timelinescraper.engines.TwitterTsEngine import TwitterTsEngine
from timelinescraper.engines.BitcoinBlockchainTsEngine import BitcoinBlockchainTsEngine

from timelinescraper.resultstore.FileSystemResultsStore import FileSystemResultsStore
from timelinescraper.resultstore.S3ResultsStore import S3ResultsStore
from timelinescraper.resultstore.ZmqResultsStore import ZmqResultsStore
from timelinescraper.resultstore.RabbitmqResultsStore import RabbitmqResultsStore
from timelinescraper.resultstore.MongoDbResultsStore import MongoDbResultsStore

workspace = "data"
engines = {
    "BitcoinBlockchainTsEngine" : BitcoinBlockchainTsEngine,
    "TradingPlatformsTradesTsEngine" : TradingPlatformsTradesTsEngine,
    "TradingPlatformsOrderbookTsEngine" : TradingPlatformsOrderbookTsEngine,
    "TwitterTsEngine" : TwitterTsEngine
}
results_stores = {
    "FileSystemResultsStore" : FileSystemResultsStore,
    "S3ResultsStore" : S3ResultsStore,
    "ZmqResultsStore" : ZmqResultsStore,
    "RabbitmqResultsStore" : RabbitmqResultsStore,
    "MongoDbResultsStore" : MongoDbResultsStore
}
scrapers = {}

def generate_name(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

'''
For an example of configuration json, see TimelineScraperManagerTest.py
'''
def create_scraper_from_config(config):
    EngineClass = engines[config["engine"]["name"]]
    engine_param_names = [param["name"] for param in EngineClass.get_config_params()]
    engine_param_values = [config["engine"][param_name] for param_name in engine_param_names]
    engine_param_values.insert(0, config["name"]) # prepending scraper name to the list
    engine = EngineClass(*engine_param_values)

    scraper = TimelineScraper(name = config["name"], workspace = workspace)

    for r_store in config["results_stores"]:
        ResultsStoreClass = results_stores[r_store["name"]]
        results_store_param_values = [
            int(float(r_store[param["name"]])) if param["type"] == "Integer"
            else r_store[param["name"]] 
            for param in ResultsStoreClass.get_config_params()]
        results_store_param_values.insert(0, workspace) # prepending workspace and name
        results_store_param_values.insert(0, config["name"])
        results_store = ResultsStoreClass(*results_store_param_values)
        scraper.add_results_store(results_store)
    
    scraper.logger.setLevel(logging.DEBUG)
    scraper.engine = engine
    

    return scraper

for config_file_name in os.listdir(workspace):
    if config_file_name.endswith(".config.txt"):
        config = None
        with open(workspace+"/"+config_file_name,'r') as config_file:
            config = json.load(config_file)
        scrapers[scraper.name] = create_scraper_from_config(config)
        scrapers[config["name"]].startScraper()

# **************************************************************************************************
# AUTH MANAGEMENT
# **************************************************************************************************
def check_authentication(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    print("check_authentication",username,password)
    return username == 'admin' and password == 'password'

def not_authenticated_response():
    """Sends a 401 response that enables basic auth"""
    return Response('You have to login with proper credentials', 
        401,
        {'WWW-Authenticate': 'Basic realm="Please insert username and password"'}
    )

def requires_auth_decorator(f):
    @wraps(f)
    def check_authentication_wrapper(*args, **kwargs):
        result = not_authenticated_response()
        auth = request.authorization
        if auth and check_authentication(auth.username, auth.password):
            result = f(*args, **kwargs)
        return result
    return check_authentication_wrapper

# **************************************************************************************************
# SERVER CONFIG
# **************************************************************************************************
static_folder_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
app = Flask(__name__, static_url_path='', static_folder=static_folder_root)
@app.route('/')
@requires_auth_decorator
def getIndex():
    return app.send_static_file('index.html')

# **************************************************************************************************
# CREATE METHODS
# **************************************************************************************************
@app.route("/api/scrapers", methods=['PUT'])
@requires_auth_decorator
def create_scraper():
    config = dict(request.get_json())

    if "name" not in config:
        scraper_name = generate_name()
        while scraper_name in scrapers:
            scraper_name = generate_name()
        config["name"] = scraper_name
    scraper_name = config["name"]
    
    scraper = None
    if scraper_name not in scrapers:
        scrapers[scraper.name] = create_scraper_from_config(config)
        filename = os.path.join(workspace,config["name"]+".config.txt")
        with open(filename,'w') as config_file:
            print("created a new scraper with config config",config)
            json.dump(config, config_file)

    scraper = scrapers[scraper_name]
    return jsonify(scraper.as_dict())

# **************************************************************************************************
# RETRIEVE METHODS
# **************************************************************************************************
@app.route("/api/engines")
@requires_auth_decorator
def get_engines():
    return jsonify({
        "engines" : [{
            "name" : engine_name,
            "params": engines[engine_name].get_config_params()
        } for engine_name in engines]
    })

@app.route("/api/resultstores")
@requires_auth_decorator
def get_results_store():
    return jsonify({
        "results_stores" : [{
            "name" : result_store_name,
            "params": results_stores[result_store_name].get_config_params()
        } for result_store_name in results_stores]
    })

@app.route("/api/scrapers", methods=['GET'])
@requires_auth_decorator
def get_scrapers():
    return jsonify({"scrapers" : [scraper.as_dict() for scraper in scrapers.values()]})

@app.route("/api/scrapers/<scraper_name>/", methods=['GET'])
@requires_auth_decorator
def get_scraper_info(scraper_name):
    result = {}
    
    if scraper_name in scrapers:
        scraper = scrapers[scraper_name]        
        result = scraper.as_dict()

    return jsonify(**result)

# **************************************************************************************************
# UPDATE METHODS
# **************************************************************************************************
@app.route("/api/scrapers/<scraper_name>/start", methods=['POST'])
@requires_auth_decorator
def start_scraper(scraper_name):
    result = {"error" : "scraper not found"}
    
    if scraper_name in scrapers:
        scraper = scrapers[scraper_name]
        scraper.startScraper()
        result = {"info" : "scraper started"}

    return jsonify(**result)

@app.route("/api/scrapers/<scraper_name>/stop", methods=['POST'])
@requires_auth_decorator
def stop_scraper(scraper_name):
    result = {"error" : "scraper not found"}
    
    if scraper_name in scrapers:
        scraper = scrapers[scraper_name]
        scraper.stopScraper()
        result = {"info" : "scraper stopped"}

    return jsonify(**result)

# **************************************************************************************************
# DELETE METHODS
# **************************************************************************************************
@app.route("/api/scrapers/<scraper_name>/", methods=['DELETE'])
@requires_auth_decorator
def del_scraper(scraper_name):
    result = {"error" : "scraper not found"}
    if scraper_name in scrapers:
        scraper = scrapers[scraper_name]
        scraper.stopScraper()
        del scrapers[scraper_name]
        os.remove(workspace+"/"+scraper_name+".config.txt")
        result = {"info" : "scraper deleted"}

    return jsonify(**result)

if __name__ == "__main__":
    app.run(debug=False, port=5048) # use host='0.0.0.0' to listen to other ports

