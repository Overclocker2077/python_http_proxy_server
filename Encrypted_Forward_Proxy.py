from functions import * 
import socket
import threading  
import gzip
# import brotli

static_routes = []

class Color:  # Colors for print function
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[94m'
    ORANGE = "\033[93m"
    RESET = '\033[0m'

class http_server():
    def __init__(self, HOST="127.0.0.1", PORT=5000, static_folder="static", log_user_data=False, session=False):
        self.routes = {}
        self.HOST = HOST
        self.PORT = PORT
        self.log_user_data = log_user_data
        self.static_folder = static_folder
        self.session = session

    # Return status code template data and file type
    def render_template(self, file_path, content_type = None, custom_headers="" ):
        status_code, template_data = read_file(file_path)
        
        if content_type == None:
            content_type = file_type(file_path)

        # # Create routes for css, js and images
        if content_type == "text/html":
            html_parser = BeautifulSoup(template_data, "html.parser")
            tag_list = [html_parser.find_all("link"), html_parser.find_all("script"), html_parser.find_all("img")]
            for tags in tag_list:
                for tag in tags:
                    if not ("/"+tag.get("src") in static_routes):
                        static_routes.append("/"+tag.get("src"))  # Route, function to retrieve data

        return (template_data, status_code, content_type, custom_headers)

    def route(self, route):   # Decorator function
        def process_routes(func): # wrapper function
            self.routes[route] = func  # Store the routes for future use
        return process_routes  # run wrapper function

    def start(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.bind((self.HOST, self.PORT))
        global web_addr
        web_addr = f"http://{self.HOST}:{self.PORT}"
        print(web_addr)
        conn.listen(1)
        # while True:
            # try:
        conn_socket, self.addr = conn.accept()

        # connection_hander(conn_socket, web_pages)
        # thread conntion handler  
        connection_handler(
            conn_socket, 
            self.addr,
            self.routes,
            self.static_folder,
            self.session,
            self.HOST,
            self.PORT,
            self.log_user_data
        ).start()
                # threading.Thread(target=connection_handler, args=(
                #                 conn_socket, 
                #                 self.addr,
                #                 self.routes,
                #                 self.static_folder,
                #                 self.session,
                #                 self.HOST,
                #                 self.PORT,
                #                 self.log_user_data),
                #                 daemon=True
                #                 ).start()   
                
            # except KeyboardInterrupt:
            #     print("Server Closing.")
    
    def register_blueprints(self, *blueprints):
        for blueprint in blueprints:
            for route, func in blueprint.routes.items():
                self.routes[route] = func

class connection_handler():
    def __init__(self, conn_socket, addr,  routes, static_folder, session, HOST, PORT, log_user_data=False):
        self.client_socket = conn_socket
        self.routes = routes  # store routes
        self.static_folder = static_folder
        self.HOST = HOST 
        self.PORT = PORT 
        self.session = session
        self.log_user_data = log_user_data
        self.addr = addr
        self.conn_target = None
        self.domain_visible_to_client = f"{HOST}:{PORT}"
        self.domain_visible_to_target = "www.coolmathgames.com"
        self.content_encoding = None

    def start(self):
        #### Run the receive_http and send_http  ####

        # The receive_from_target and receice_from_client will be ran in parallel
        # threading.Thread(target=self.receive_data_from_target).start()
        threading.Thread(target=self.receive_data_from_client).start()

    def content_decode(self, content):
        # if self.content_encoding == "br":
        #     return brotli.decompress(content)
        try:
            return gzip.decompress(content)
        except:
            return unicode_decoder(content)
    
    def content_encode(self,content):
        # if self.content_encoding == "br":
        #     return brotli.compress(content)
        if self.content_encoding == "gzip":
            return gzip.compress(content)
        return unicode_decoder(content)
    
    def receive_data_from_target(self):   # The send_data_to_client will be ran inside this method
        while True:
            if "closed" in str(self.conn_target):
                self.client_socket.close()
                quit(0)
            
            REQUEST = self.conn_target.recv(2048)
            threading.Thread(target=self.process_request_from_target, args=(REQUEST, )).start()

    def process_request_from_target(self, REQUEST):
        if b"http" in REQUEST:
            parsed_request = response_parser(unicode_decoder(REQUEST))
            parsed_request_dict = isinstance(parsed_request, dict)

            if REQUEST == b"":
                self.conn_target.close()
                quit(0)

            # print(Color.GREEN, f"######### Receiving request from Target ##########\n\n",
            #     f"{unicode_decoder(REQUEST)}\n\n{self.domain_visible_to_target}\n\n{parsed_request}", Color.RESET)

            if not parsed_request_dict:

                request_param = {
                    "Type": "Response",
                    "Status_code": parsed_request[1],
                    "Content": parsed_request[4],
                }

                for key, value in parsed_request[3].items():
                    # if key != "Content-Security-Policy-Report-Only" and key != "Cross-Origin-Opener-Policy" and key != "Transfer-Encoding ":
                    if key != "Transfer-Encoding":
                        request_param[key] = value

                # print(Color.RED, make_request(**request_param).decode(), Color.RESET)
                self.send_data_to_client(make_request(**request_param))
                # self.conn_target.close()  
        else: 
            self.send_data_to_client(REQUEST)

    def receive_data_from_client(self): #  The send_data_target will be ran inside this method
        while True:
            # If client socket closed ---> Terminate target sockets
            if "closed" in str(self.client_socket):
                self.conn_target.close()
                quit(0)

            REQUEST = self.client_socket.recv(2048)
            # print(REQUEST)
            threading.Thread(target=self.process_request_from_client, args=(REQUEST, )).start()

    def process_request_from_client(self, REQUEST):
        if REQUEST == b"":
            self.conn_target.close()
            quit(0)
            
        parsed_request = request_parser(unicode_decoder(REQUEST))
        # Check if chunk encoding is active

        # Normal Request 
        if  parsed_request:   
            endpoint_path = parsed_request[1]
            print(endpoint_path)

            # print(Color.YELLOW, "######### Receiving request from Client  ##########\n\n",
            #     f"{parsed_request}\n\n{self.domain_visible_to_target}\n{endpoint_path}", Color.RESET)

            if not self.conn_target:
                self.conn_target = connect_to_target(self.domain_visible_to_target, 443)
                threading.Thread(target=self.receive_data_from_target).start()                

            request_param = {
                "Type": "request",
                "Route": endpoint_path,
                "Host": self.domain_visible_to_target,
                "Method": parsed_request[0],
            }
            # Add remaining headers
            for key, value in parsed_request[3].items():
                if key != "Upgrade-Insecure-Requests" and key != "Host" and key != "Transfer-Encoding":
                # if key != "Host":
                    request_param[key] = value

            self.send_data_to_target(make_request(**request_param))
            
    def send_data_to_target(self, request):
        print("######### Sending to Target ##########")
        self.conn_target.send(request)
        # print(self.content_decode(request))

    def send_data_to_client(self, request):
        print("######### Sending to Client ##########")
        self.client_socket.send(request)
        # print(self.content_decode(request))

    def log_data(self):
        ...

app = http_server(HOST="192.168.1.194")
# app = http_server()
app.start()

# @app.route("/")
# def home_page():
#     return "Welcome to the homepage"

# a = app.return_routes()
# print(a)

# result = a["/"]()
# print(result)