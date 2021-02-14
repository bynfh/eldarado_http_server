import argparse
import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
import LoadData
import config
##############################ARGPARSE##############################
parser = argparse.ArgumentParser(description='Eldarado_Api')
parser.add_argument('--html', default=config.HTML, type=str,
                    help='Output result in html or json.'
                         ' You may input true, 1, ok, y or False, 0'
                         ' default = True')
parser.add_argument('--debug', default=config.DEBUG, type=str,
                    help='On or Off debug logging lvl, default = False')
parser.add_argument('--host', default=config.HOST, type=str,
                    help='Ip address server, default = 127.0.0.1')
parser.add_argument('--port', default=config.PORT, type=int,
                    help='Port for server, default = 8080')
parser.add_argument('--path_to_csv', default=config.PATH_TO_CSV, type=str,
                    help='Path to csv data, default = ./sorted_recommends.csv')
parser.add_argument('--max_rows_csv', default=config.MAX_ROWS_FROM_CSV, type=float,
                    help='max rows from csv load, default = infinity')
args = parser.parse_args()
##############################CONSTANT##############################
html_set = ['true', '1', 'ok', ]
HOST = args.host
PORT = args.port
PATH_TO_CSV = args.path_to_csv
MAX_ROWS_CSV = args.max_rows_csv
HTML = True if args.html.lower() in html_set else False
##############################ARGPARSE##############################
#################################LOG################################
DebugOn = ['1', 'true', 'y']
logger = logging.getLogger('Eldarado_api_main')
FORMAT = '%(asctime)s  %(name)s [%(levelname)s]: %(message)s'
file_handler = logging.FileHandler('Eldarado_api_main.log', 'a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(FORMAT))

# Choose level logging (DEBUG или INFO)
if args.debug.lower() in DebugOn:
    logging.basicConfig(level=logging.DEBUG,
                        format=FORMAT,
                        datefmt='%Y/%m/%d %H:%M')
else:
    logging.basicConfig(level=logging.INFO,
                        format=FORMAT,
                        datefmt='%Y/%m/%d %H:%M')
logger.addHandler(file_handler)


class CustomRequest(BaseHTTPRequestHandler):
    """For http request"""
    def _set_headers(self):
        """
        Private method.
        Set response status and headers
        If HTML == 'True' then header == html
        else header == json
        """
        self.send_response(200)
        if HTML:
            self.send_header("Content-type", "text/html")
        else:
            self.send_header("Content-type", "application/json")
        self.end_headers()

    @staticmethod
    def _HtmlResponse(SKU: str, NearbyRecommends: float) -> str:
        """
        Private method.
        Get data about recommends and wrap in html.
        """
        HtmlResp = f'<html><body><h1>For this product:{SKU}.</h1>'
        # Get Data from dict and split str
        Recommends = DataFromCsv.get(SKU, f'No recommends for {SKU}').split(';')
        for Recommend in Recommends:
            # Recommend split on space. Delete empty str from list.
            List_Recommend = list(filter(lambda x: '' if x == '' else x, Recommend.split(' ')))
            # For pass recommend if his number less than from request
            if List_Recommend and NearbyRecommends and float(List_Recommend[1]) < NearbyRecommends:
                pass
            else:
                HtmlResp += f"<p>{Recommend}</p>"
        HtmlResp += '</body></html>'
        return HtmlResp

    @staticmethod
    def _JsonResponse(SKU: str, NearbyRecommends: float) -> str:
        """
        Private method.
        Get data about recommends and wrap in json.
        """
        JsonResp = {SKU: []}
        # Get Data from dict and split str
        Recommends = DataFromCsv.get(SKU, f'No recommends').split(';')
        for Recommend in Recommends:
            # Recommend split on space. Delete empty str from list.
            RecommendSplit = list(filter(lambda x: '' if x == '' else x, Recommend.split(' ')))
            # For pass recommend if his number less than from request
            if RecommendSplit and NearbyRecommends and float(RecommendSplit[1]) < NearbyRecommends:
                pass
            elif RecommendSplit:
                JsonResp[SKU].append([RecommendSplit[0], RecommendSplit[1]])
        return json.dumps(JsonResp)

    def do_GET(self):
        """Method for processing get requests"""
        # URL search /get_recommends/SKU/
        if re.search('\/get_recommends\/(\w+)\/*', self.path):
            NumbNearRec = None
            # Get SKU str from URL
            SKU = re.search('\/get_recommends\/(\w+)\/*', self.path).groups()[0]
            # Check if in URL is proximity of recommendations
            if re.search('\/get_recommends\/(\w+)\/*(\d*[,.]\d*)', self.path):
                # Do float from str
                NumbNearRec = re.search('\/get_recommends\/(\w+)\/*(\d*[,.]\d*)', self.path).groups()[1]
                NumbNearRec = NumbNearRec.replace(',', '.')
                NumbNearRec = float(NumbNearRec)
            self._set_headers()
            # Generate Response Html or json for SKU and Numb
            Response = self._HtmlResponse(SKU, NumbNearRec) if HTML else self._JsonResponse(SKU, NumbNearRec)
            self.wfile.write(bytes(Response, encoding='UTF-8'))
        # Nothing to do if URL == '/favicon.ico'
        elif self.path == '/favicon.ico':
            pass
        else:
            self.send_response(404)


def RunServer(host="localhost", port=8000, server_class=HTTPServer, handler_class=CustomRequest):
    """Run simple http server"""
    server_address = (host, port)
    Server = server_class(server_address, handler_class)
    logger.info(f"Starting http server on {host}:{port}")
    try:
        Server.serve_forever()
    except KeyboardInterrupt:
        Server.server_close()
        logger.warning("You stopped server")


if __name__ == '__main__':
    logger.info(f"Starting to get Data")
    try:
        # Get data from file csv and load to dict
        DataFromCsv = LoadData.GetDataFromCsv(PATH_TO_CSV, MAX_ROWS_CSV)
        logger.info(f"Data obtained")
        # Run server for processing requets
        RunServer(HOST, PORT)
    except FileNotFoundError:
        logger.exception(f"Such file not founded:{PATH_TO_CSV}")
    except KeyboardInterrupt:
        logger.warning("You stopped program")
