import urllib.request as urlreq
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote
from http.server import *
from database import Database
import re
import json


class myHTTPRequestHandler(BaseHTTPRequestHandler):
    db = Database()

    def do_HEAD(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        try:
            request_info = urlparse(self.path)
            request_path = request_info.path.strip('/').split('/')

            if request_info.query:
                request_query = {param.split('=')[0]: param.split(
                    '=')[1] for param in request_info.query.split('&')}
                if 'page' in request_query:
                    self.db.set_page(int(request_query['page']))
                # if 'date' in request_query:
                #     request_query['date'] = datetime.strptime(request_query['date'], '%Y/%m/%d')
            else:
                request_query = []

            if request_path[0] == 'products':
                if len(request_path) == 1:
                    if 'name' in request_query:
                        #     if 'date' in request_query:
                        #         data = self.db.select_product_name_date(unquote(request_query['name']),request_query['date'])
                        #     else:
                        #         data = self.db.select_product_name(unquote(request_query['name']))
                        # elif 'date' in request_query:
                        #     data = self.db.select_products_date(request_query['date'])
                        data = self.db.select_product_name(
                            unquote(request_query['name']))
                    else:
                        data = self.db.select_all_products()
                elif len(request_path) == 2:
                    data = self.db.select_product_id(int(request_path[1]))
                else:
                    raise AttributeError
            elif request_path[0] == 'movies':
                if len(request_path) == 1:
                    if 'name' in request_query:
                        data = self.db.select_movie_name(
                            unquote(request_query['name']))
                    else:
                        data = self.db.select_all_movies()
                elif len(request_path) == 2:
                    data = self.db.select_movie_id(int(request_path[1]))
                else:
                    raise AttributeError
            else:
                raise ValueError

            if not data:
                raise IOError
            else:
                response_json = json.dumps(data)
                self.send_response(200, 'OK')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                # send json
                self.wfile.write(response_json.encode())

        except IOError:
            self.send_error(404, 'Page Not Found')
        except AttributeError:
            self.send_error(400, 'Bad Request')
        except ValueError:
            self.send_error(400, 'Bad Request')

    def parse_body(self):
        content_len = int(self.headers.get('Content-Length'))
        raw_body = self.rfile.read(content_len).decode()
        request_body = dict(re.findall(
            r"name=\"(\w*)\"\s*([\w/ -]*)\s*", raw_body))
        return request_body

    def get_address_string(self):
        string = self.server.server_address[0] + \
            ':' + str(self.server.server_address[1])
        return string

    def do_POST(self):
        request_info = urlparse(self.path)
        request_path = request_info.path.strip('/').split('/')
        try:
            if len(request_path) == 1:
                request_body = self.parse_body()
                if request_path[0] == 'products':
                    if 'product_name' not in request_body or 'expiration_date' not in request_body:
                        raise ValueError
                    else:
                        id = self.db.insert_product(
                            unquote(request_body['product_name']), request_body['expiration_date'])
                elif request_path[0] == 'movies':
                    if 'movie_title' not in request_body or 'movie_genre' not in request_body:
                        raise ValueError
                    else:
                        id = self.db.insert_movie(
                            unquote(request_body['movie_title']), unquote(request_body['movie_genre']))
                else:
                    raise IOError
            else:
                raise IOError
            response_body = {'id': id}
            response_body.update(request_body)
            response_json = json.dumps(response_body)

            self.send_response(201, 'Created')
            self.send_header('Content-type', 'application/json')

            location_string = 'http://' + self.get_address_string() + '/' + \
                request_path[0] + '/' + str(id)
            self.send_header('Location', location_string)
            self.end_headers()
            # send json
            self.wfile.write(response_json.encode())

        except ValueError:
            self.send_error(400, 'Bad Request')
        except IOError:
            self.send_error(404, 'Page Not Found')

        # insert body -> return id

    def do_PUT(self):
        request_info = urlparse(self.path)
        request_path = request_info.path.strip('/').split('/')
        try:
            if len(request_path) == 1:
                raise TypeError
            elif len(request_path) == 2:
                request_body = self.parse_body()
                if request_path[0] == 'products':
                    if 'product_name' not in request_body or 'expiration_date' not in request_body:
                        raise ValueError
                    else:
                        try:
                            id = self.db.insert_product_id(
                                int(request_path[1]), unquote(request_body['product_name']), request_body['expiration_date'])
                            self.send_response(201, 'Created')
                            self.send_header(
                                'Content-type', 'application/json')
                            self.end_headers()
                        except:
                            self.db.update_product(int(request_path[1]), unquote(
                                request_body['product_name']), request_body['expiration_date'])
                            self.send_response(204, 'No Content')
                            self.send_header(
                                'Content-type', 'application/json')
                            self.end_headers()
                elif request_path[0] == 'movies':
                    if 'movie_title' not in request_body or 'movie_genre' not in request_body:
                        raise ValueError
                    else:
                        try:
                            id = self.db.insert_movie_id(
                                int(request_path[1]), unquote(request_body['movie_title']), unquote(request_body['movie_genre']))
                            self.send_response(201, 'Created')
                            self.send_header(
                                'Content-type', 'application/json')
                            self.end_headers()
                        except:
                            self.db.update_movie(int(request_path[1]), unquote(
                                request_body['movie_title']), unquote(request_body['movie_genre']))
                            self.send_response(204, 'No Content')
                            self.send_header(
                                'Content-type', 'application/json')
                            self.end_headers()
                else:
                    raise IOError
            else:
                raise IOError
        except ValueError:
            self.send_error(400, 'Bad Request')
        except IOError:
            self.send_error(404, 'Page Not Found')
        except TypeError:
            self.send_error(405, 'Method Not Allowed')
        # insert -> error? -> update

    def do_DELETE(self):
        request_info = urlparse(self.path)
        request_path = request_info.path.strip('/').split('/')
        try:
            if len(request_path) == 1:
                raise TypeError
            elif len(request_path) == 2:
                if 'products' == request_path[0]:
                    if not self.db.select_product_id(int(request_path[1])):
                        raise EOFError
                    else:
                        self.db.delete_product_id(int(request_path[1]))
                elif 'movies' == request_path[0]:
                    if not self.db.select_movie_id(int(request_path[1])):
                        raise EOFError
                    else:
                        self.db.delete_movie_id(int(request_path[1]))
                else:
                    raise IOError
                # self.db.delete_product_id(int(request_path[1]))
            else:
                raise IOError
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        except ValueError:
            self.send_error(400, 'Bad Request')
        except (IOError, EOFError):
            self.send_error(404, 'Not Found')
        except TypeError:
            self.send_error(405, 'Method Not Allowed')


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    try:
        server_address = ('', 8000)
        server = server_class(server_address, handler_class)
        server.serve_forever()
    except:
        server.socket.close()


run(handler_class=myHTTPRequestHandler)
