import urllib.request as urlreq
import urllib.parse #quote
from http.server import *
import time
import json
import re

class myHTTPRequestHandler(BaseHTTPRequestHandler):
    metrics = {"latency":0.0,"success":0,"fail":0}
    def do_HEAD(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        self.do_HEAD()
        if "/metrics" in self.requestline:
            self.wfile.write(json.dumps(self.metrics).encode())
        else:
            startt = time.time()
            index = open("index.html","rb")
            self.wfile.write(index.read())
            index.close()
            endt = time.time()
            latency = endt - startt
            self.log_message("%.6f",latency)

    def log_message(self,format,*args):
        log = open("log.txt",'a')
        if 'f' in format:
            self.metrics["latency"] += args[0]
            self.metrics["latency"] /= 2
        else:
            if '200' in args:
                self.metrics["success"] += 1
            else:
                self.metrics["fail"] += 1
            log.write(self.log_date_time_string())
        log.write(format%args)
        log.write('\n')
        log.close()
    def do_POST(self):
        startt = time.time()
        self.do_HEAD()
        description,quote = self.get_quote()
        sentiment = self.get_sentiment(text = description+'\n'+quote)
        self.wfile.write(bytes('<p>'+description+'</p>','UTF-8'))
        self.wfile.write(bytes('<p>'+quote+'</p>','UTF-8'))
        self.wfile.write(bytes('<p>'+sentiment+'</p>','UTF-8'))
        index = open("index.html","rb")
        self.wfile.write(index.read())
        index.close()
        endt = time.time()
        latency = endt - startt
        self.log_message("%.6f",latency)
    def get_quote(self):
        wiki_endpoint = 'https://en.wikipedia.org/w/api.php'#"https://test.wikipedia.org/w/api.php"  #https://en.wikipedia.org/w/api.php
        opinionated_quotes_endpoint = "https://opinionated-quotes-api.gigalixirapp.com/v1/quotes"
        req = urlreq.urlopen(opinionated_quotes_endpoint)
        quote = json.load(req)['quotes'][0]
        req.close()
        while 'author' not in quote.keys():
            req = urlreq.urlopen(opinionated_quotes_endpoint)
            quote = json.load(req)['quotes'][0]
            req.close()
        else:
            author = re.search(r"((\w+ *)*)",quote["author"]).group(1)

        search_string = "?action=opensearch&format=json&search=" + urllib.parse.quote(author) + "&limit=1"
        search_string = '?'+urllib.parse.urlencode({'action':'opensearch','format':'json','search':author,'limit':'3'},quote_via=urllib.parse.quote)
        '''
        search_result[1] = title of result
        search_result[2] = description of result
        '''
        req = urlreq.urlopen(wiki_endpoint + search_string)
        search_result = json.load(req)
        req.close()
        for description in search_result[2]:
            if 'may refer to' in description:
                pass
            else:
                return description, quote['quote']
        return "", quote['quote']
    def get_sentiment(self,text):
        message = {"input":text}
        data = json.dumps(message)
        api_key = json.load(open("creds.json"))["key"]
        req = urllib.request.Request("https://digitalowl.org/api/classify/sentiment",data.encode())
        req.add_header("Content-Type","application/json")
        req.add_header("api_key",api_key)
        response = urllib.request.urlopen(req)
        payload = json.load(response)
        response.close()
        return payload["sentiment"]
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
run(handler_class=myHTTPRequestHandler)
