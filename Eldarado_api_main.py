import argparse
import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
import LoadData
##############################ARGPARSE##############################
parser = argparse.ArgumentParser(description='Eldarado_Api')
parser.add_argument('--html', default='True', type=str,
                    help='Output result in html or json.'
                         ' You may input true, 1, ok, y or False, 0'
                         ' default = True')
parser.add_argument('--debug', default='0', type=str,
                    help='On or Off debug logging lvl, default = False')
parser.add_argument('--host', default='127.0.0.1', type=str,
                    help='Ip address server, default = 127.0.0.1')
parser.add_argument('--port', default=8080, type=int,
                    help='Port for server, default = 8080')
parser.add_argument('--path_to_csv', default='./sorted_recommends.csv', type=str,
                    help='Path to csv data, default = ./sorted_recommends.csv')
parser.add_argument('--max_rows_csv', default=float("inf"), type=float,
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

# choose level logging (DEBUG или INFO)
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
    def _set_headers(self):
        self.send_response(200)
        if HTML:
            self.send_header("Content-type", "text/html")
        else:
            self.send_header("Content-type", "application/json")
        self.end_headers()

    @staticmethod
    def _HtmlResponse(SKU, NearbyRecommends):
        HtmlResp = f'<html><body><h1>For this product:{SKU}. Recommendations.</h1>'
        Recommends = DataFromCsv.get(SKU, f'No recommends for {SKU}').split(';')
        for Recommend in Recommends:
            Digit = list(filter(lambda x: '' if x == '' else x, Recommend.split(' ')))
            if Digit and NearbyRecommends and float(Digit[1]) < NearbyRecommends:
                pass
            else:
                HtmlResp += f"<p>{Recommend}</p>"
        HtmlResp += '</body></html>'
        return HtmlResp

    @staticmethod
    def _JsonResponse(SKU, NearbyRecommends):
        JsonResp = {SKU: []}
        Recommends = DataFromCsv.get(SKU, f'No recommends').split(';')
        for Recommend in Recommends:
            RecommendSplit = list(filter(lambda x: '' if x == '' else x, Recommend.split(' ')))
            if RecommendSplit and NearbyRecommends and float(RecommendSplit[1]) < NearbyRecommends:
                pass
            elif RecommendSplit:
                JsonResp[SKU].append([RecommendSplit[0], RecommendSplit[1]])
        return json.dumps(JsonResp)

    def do_GET(self):
        if re.search('\/get_recommends\/(\w+)\/*', self.path):
            NumbNearRec = None
            SKU = re.search('\/get_recommends\/(\w+)\/*', self.path).groups()[0]
            if re.search('\/get_recommends\/(\w+)\/*(\d*[,.]\d*)', self.path):
                NumbNearRec = re.search('\/get_recommends\/(\w+)\/*(\d*[,.]\d*)', self.path).groups()[1]
                NumbNearRec = NumbNearRec.replace(',', '.')
                NumbNearRec = float(NumbNearRec)
            self._set_headers()
            Response = self._HtmlResponse(SKU, NumbNearRec) if HTML else self._JsonResponse(SKU, NumbNearRec)
            self.wfile.write(bytes(Response, encoding='UTF-8'))
        elif self.path == '/favicon.ico':
            pass
        else:
            self.send_response(404)


def RunServer(host="localhost", port=8000, server_class=HTTPServer, handler_class=CustomRequest):
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
        DataFromCsv = LoadData.GetDataFromCsv(PATH_TO_CSV, MAX_ROWS_CSV)
        logger.info(f"Data obtained")
        RunServer(HOST, PORT)
    except FileNotFoundError:
        logger.exception(f"Such file not founded:{PATH_TO_CSV}")
    except KeyboardInterrupt:
        logger.warning("You stopped program")


#'002m5QjMsF', '002NT3R0tf', '002RhefPpG', '002ZvGHE2o', '
