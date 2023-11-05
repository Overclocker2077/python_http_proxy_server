import json
from bs4 import BeautifulSoup
import random
import socket
import ssl
import re

encode_dict = {
    r" ": "+",
    r"!": r"%21",
    r'"': r"%21",
    r"#": r"%25",
    r"$": r"%24+",
    r"%": r"%25",
    r"&": r"%26",
    r"'": r"%27",
    r"(": r"%28",
    r")": r"%29",
    r"+": r"%2B",
    r",": r"%2C",
    r"/": r"%2F",
    r":": r"%3A",
    r";": r"%3B",
    r"<": r"%3C",
    r"=": r"%3D",
    r">": r"%3E",
    r"?": r"%3F",
    r"@": r"%40",
    r"[": r"%5B",
    r"\\": r"%5C",
    r"]": r"%5D",
    r"^": r"%5E",
    r"`": r"%60",
    r"{": r"%7B",
    r"|": r"%7C",
    r"}": r"%7D",
    r"~": r"%7E"
}

# class Error(Exception): print("Error")

def decode_url(data):
    data = list(data)
    for key, value in encode_dict.items():
        for i in range(len(data)):
            if data[i:i+len(value)] == list(encode_dict[key]):
                data[i:i+len(value)] = key 
    return "".join(data)

def encode_url(data):
    data = list(data)
    for key, value in encode_dict.items():
        for i in range(len(data)):
            if data[i] == key:
                data[i] = value
    return "".join(data)

def request_parser(raw_request):
    request_lines = str(raw_request).split('\r\n')
    request_line = request_lines[0]
    # Extract request method, endpoint path, and protocol version
    match = re.match(r'(\w+) (\S+) (HTTP/\d+\.\d+)', request_line)
    if match:
        request_method, endpoint_path, protocol_version = match.groups()
    else:
        raise ValueError("Invalid request line")
    # Parse headers and store them in a dictionary
    headers = {}
    for line in request_lines[1:]:
        if not line:
            break  # Headers end with an empty line
        key, value = line.split(': ', 1)
        headers[key] = value
    # Extract the request body (data)
    data = request_lines[-1]
    return [request_method, endpoint_path, protocol_version, headers, data]

def response_parser(raw_response):
    response_lines = raw_response.split('\r\n')
    # Extract the status line to get status code and reason phrase
    status_line = response_lines[0].split("\n")[0]
    match = re.match(r'HTTP/(\d+\.\d+) (\d+) (.+)', status_line)
    if match:
        protocol_version, status_code, reason_phrase = match.groups()
    else:
        raise ValueError("Invalid status line")
    # Parse headers and store them in a dictionary
    headers = {}
    for line in response_lines[1:-1]:
        if not line:
            break  # Headers end with an empty line
        key, value = line.split(': ', 1)
        headers[key] = value
    # Extract the response body (data)
    data = response_lines[-1]
    return [protocol_version, int(status_code), reason_phrase, headers, data]


# request_1 = 'HTTP/1.1 200 OK\r\nDate: Wed, 01 Nov 2023 23:20:45 GMT\r\nContent-Type: text/html; charset=UTF-8\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\nCF-Ray: 81f7dec6ad1507a0-IAD\r\nCF-Cache-Status: HIT\r\nAge: 13097\r\nCache-Control: max-age=86400, public\r\nContent-Language: en\r\nExpires: Sun, 19 Nov 1978 05:00:00 GMT\r\nLast-Modified: Wed, 01 Nov 2023 19:41:57 GMT\r\nSet-Cookie: cmg_country=US;path=/;\r\nVary: Accept-Encoding\r\nSet-Cookie: cmg_region=VA;path=/;\r\nSet-Cookie: cmg_city=Herndon_VA;path=/;\r\nSet-Cookie: cmg_city1=Herndon;path=/;\r\nX-Cache-Hits: 0\r\nX-Content-Type-Options: nosniff\r\nX-Drupal-Cache: HIT\r\nX-Frame-Options: SAMEORIGIN\r\nX-UA-Compatible: IE=edge\r\nX-Varnish: 4992517\r\nX-Varnish-Cache: MISS\r\nServer: cloudflare\r\nContent-Encoding: gzip\r\n\r\n642\r\n\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03\x8cVmS\xe38\x12\xfe\x9e_!2[\x91D\x8c\x1c\xd8\x9b\xba\xaa\x18\x91e\x18\xaa\x8e*\x16\xb6\x16v\xf7\xae\x80I\t\xab\x1d\x8b\xb1%\xaf\xa4\x04\xb2I\xfe\xfb\x95\xec\xbcA`\xef\xbe\xb8\xec\xd6\xa3\xee\xa7[\xfd\xb4\xd5:\xde\xfbz}v\xfb\x9f_\xceQ\xee\xcb\xe2\xe48<Q!\xf4\x88\xb7A\xb7\x91T\x96\xb7\x0bo\xdb\xa8\xb2\x90\xa9\x17\xdeN\x8d\xf6\xa0}\x1f\xe5\xdeW\xfd8\xae\xc6\xb6`\xc6\x8eb\xeb\\|\xc8zqi\xe4\xb8\x00\x17/\x811B2\xddE\xcb4\xf6`K\x17#\x94\x19\x91\xad\x01/e\xa1\x1dKM\x19\x07s\xdcc\x871Bf\xb4^7\xa3\x8a\x95\x10k\xf7\t!+3\xb7^x~~f\xcf?\xd6\xbe\x8fz\xbd^\xdc;\x8c\xad\xcc\x0e\\\x9aC)>!\xd4\xbc\xac\xe1\xcdg\rG\xc8)\xb3\xa1\x18\xbc\xd6\xf6`m\x02\x857\xff\x01\xc0O+\xa81\xdf\xcdGd\xfe\x11\xf7\x8e\xe2\xb0\x1e\xa7\xc6\xc2\'\x84^\x9c\xfc\x00z\x18\xff\xfb\xe7\xcb\x9b%\xe76\xb2P\xf0\xb6\xa9\xbc*\xd5_ \xdb\'\xc79\x08yr\xbcwp\x80n\xbc\xb0\x1e\xfd\xfe\xc75:uS\x9d\xa2\x9bRX\x7ff$\xa0\x83\x83\x93c\x97ZUy\x14\xc8q\xec\xe1\xc5\xc7Ob"\x1a+FJr<y6\x01\x8dOZ\xcfJK\xf3\xcc\x86\x93g3L\x8d\x04\xfe\xd6\x80\xe6sD\xb2\xb1N\xbd2\x9aP4kM\x84E"M\xcdX\xfb\xa1\x92\xfc\x9f\x87GG\xbd\xa3\xa85\x01\xeb\x94\xd1\x88\xa3C\xf69j9\xf0^\xe9\x91\x1bzS\x80\x15:\x05\x1e\x8e&j\x15\xea\xd1\n;\xdd\xb6\x7f\x0e\xf6\xb1\x83!\xbc(\x17v\r\x9f\xfe\x1c\x83\x9d\xf2L\x14\x0e\xa2\x96rCW\t~\x18\xb5r%a\x08\x05\x94\xa0=\xc7\x8fFN\xf1k\xe3\xd0\xf9i\x01\x88#l*\x91*?\xed\xf7\xd0\x9e*+c\xbd\xd0>\xc9T\xe1\xc1\xf6EQ\xe5\x82,\x11\xbcG\xb7!\x8f"\xfd>\xb2f\xace_\x1b\r[K8j\xc5\xfb\xe8\xeb5\xba\xba\xbeE\xe7_/n\xd1\x97\xf3\xcb\xeb?\xd0\xed\xbf.n\xd0\xe5\xc5\xd59\xda\x8f[\xd9\x92\xb4\xe4\xd2\xa4\xe3@)ZV\xfb\xbc\xe0\x92\xd5y\xdd@\x01\xa97\x96\xe0O\xab\x93\xa0Q]\xfd\xd9;U\xe8o\xaa?\xb3\xe0\xc7V\xa3wP\x8bh\xa7\xb0\xefl\xdc\xc1,\xa2\xdd\xea\xed\xee\xc33\xdc\xdd\xc5u\xf1\x02/\xa2'
# request_2 = 'GET /www.coolmathgames.com HTTP/1.1\r\nHost: 192.168.1.194:5000\r\nConnection: keep-alive\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nDNT: 1\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en-US,en;q=0.9\r\nCookie: ASP.NET_SessionId=pxuqso4yu5rjd30vxy3cwfy0; cmg_country=US; cmg_region=VA; cmg_city=Herndon_VA; cmg_city1=Herndon\r\n\r\n'
# request_3 = """HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:  922\r\nDate: Thu, 02 Nov 2023 21:41:21 GMT\r\nCF-Ray: 81ff8a866ec28244-IAD\r\nCF-Cache-Status: HIT\r\nAge: 3966\r\nCache-Control: max-age=86400, public\r\nContent-Language: en\r\nExpires: Sun, 19 Nov 1978 05:00:00 GMT\r\nLast-Modified: Thu, 02 Nov 2023 20:35:11 GMT\r\nSet-Cookie: cmg_city1=Washington;path=/;\r\nVary: Accept-Encoding\r\nX-Cache-Hits: 0\r\nX-Content-Type-Options: nosniff\r\nX-Drupal-Cache: MISS\r\nX-Frame-Options: SAMEORIGIN\r\nX-UA-Compatible: IE=edge\r\nX-Varnish: 3557396\r\nX-Varnish-Cache: MISS\r\nServer: cloudflare\r\nContent-Encoding: gzip\r\n▼♥ÂVmSÃ£8↕Ã¾Â_!2[ÂDÂ∟ÃÂÂºÂª↑Âe↑ÂªÂ*▬Â¶▬vÃ·Â®ÂI  Â«↔ÂÂ±%Â¯Â¤♦Â²IÃ¾Ã»ÂÃ¬Â¼A`Ã¯Â¾Â¸Ã¬ÃÂ£Ã®Â§[Ã½Â´Ã:ÃÃ»z}vÃ»Â_ÃQÃ®ÃÃ¢Ã¤8<Q!Ã´ÂÂ·AÂ·ÂTÂÂ·GÃ)Â³Â¡↑Â¼ÃÃ¶`m☻Â7Ã¿☺ÃO+Â¨1ÃÃGdÃ¾◄Ã·ÂÃ¢Â°▲Â§ÃÃ'Â^ÂÃ¼z↑Ã¿Ã»Ã§ÃÂ%Ã§6Â²PÃ°Â¶Â©Â¼*Ã_ Ã'ÃyrÂ¼wpÂnÂ¼Â°▲Ã½Ã¾Ã5:uSÂÂ¢ÂRXf$Â ÂÂÂcÂZUy¶ÃqÃ¬Ã¡ÃÃOb"→+FJr<y6☺ÂOZÃJKÃ³ÃÂÂg3LÂ♦Ã¾ÃÂÃ¦sDÂ²Â±NÂ½2ÂP4kMÂE"MÃXÃ»Â¡ÂÃ¼ÂÂGGÂ½Â£Â¨5☺Ã«ÂÃÂÂ£CÃ¶9j9Ã°^Ã©ÂSÂ§:♣▲Â&j§ÃªÃ8jÃÃ»Ã¨Ã«5ÂºÂºÂ¾EÃ§_/nÃÂÃ³ÃÃ«?ÃÃ­Â¿.nÃÃ¥ÃÃ9ÃÂ[ÃÂÂ´Ã¤ÃÂ¤Ã£@)ZVÃ»Â¼Ã ÂÃyÃ@☺Â©7ÂÃ OÂ«ÂÂ Q]Ã½Ã;UÃ¨oÂª?Â³Ã ÃVÂ£wPÂhÂ§Â°Ã¯lÃÃ,Â¢ÃÃªÃ­Ã®Ã3ÃÃ"""

# #print(response_parser(request_1))
# print(response_parser(request_3))

def formData_parser(requests):
    form_data = {}
    requests_lines = requests.split("\n")
    form_data_split1 = requests_lines[len(requests_lines)-1].split("&")
    form_data_split2 = [data.split("=") for data in form_data_split1]
    for i in range(len(form_data_split2)):
        form_data[form_data_split2[i][0]] = decode_url(form_data_split2[i][1])
    return form_data

def rand_key(key_len):
    return [random.randint(1,127) for _ in key_len]

def xor_cipher(data, key):         # key must be a list of numbers
    if not ("list" in str(type(data))):
        data = list(bytes(data.encode()))
    for _, key_index in enumerate(key):
        for count, data_index in enumerate(data):
            data[count] = data_index^key_index
    return data

def decode(data):   # number list to string list 
    for count,index in enumerate(data):
        data[count] = chr(index)
    return data 

def encode(data):   #  string to number list
    if "list" in str(type(data)):
        data = "".join(data)
    return list(bytes(data.encode()))

def json_parser(requests):  # JSON parser for requests 
    start_line = None
    form_data = {}
    requests_lines = requests.split("\n")
    for i in range(len(requests_lines)):  # starting line for the json data
        if requests_lines[i] == "": 
            start_line = i 
            break
    return json.loads("".join(requests_lines[start_line:]))

content_types_dict = {
                      "html": "text/html", 
                      "css": "text/css", 
                      "mp4": "video/mp4", 
                      "png": "image/png", 
                      "js": "application/javascript", 
                      "json": "application/json",
                      "jpg": "image/jpeg",
                      "jpeg": "image/jpeg"
                      }

def file_type(file_name):  # returns Content-Types for file
    file_extension = file_name.split(".")[1]
    for key, value in content_types_dict.items():
        if key == file_extension:
            return value
    
    print("Unsupported file type")
    return "text/plain"

def process_json(json_data):
    data_dict = [json.loads(json_data) if "str" in str(type(json_data)) else json_data][0]
    process_json_string = []
    for key, value in data_dict.items():
        # Handle duplicate values
        if isinstance(value, list): 
            process_json_string.append("".join([f"{key}: {dup_value}\r\n" for dup_value in value]))
        elif key != "" and value != "":
            process_json_string.append(f"{key}: {value}\r\n")
    processed_json_string ="".join(process_json_string)
    return processed_json_string

# Rewrite the transfer encoding domain  
def transfer_encoding_parser(request):  # WIP
    # Split the string into lines
    lines = request.split('\r\n')
    headers = {}

    # Iterate through each line and parse header fields
    for line in lines:
        # Split each line into key-value pairs using a regex
        header_parts = re.split(r':\s*', line, 1)
        
        if len(header_parts) == 2:
            key = header_parts[0]
            value = header_parts[1]
            headers[key] = value

    return headers

def end_of_transfer_encoding(request):
    if re.compile(r"0\r\n\r\n").search(request):
        return True
    return False

# raw_request = '-yJS4I80wRGCWePPk3sT4bf0; expires=Sat, 27-Apr-2024 22:20:58 GMT; path=/; domain=.google.com; Secure; HttpOnly; SameSite=none\r\nAlt-Svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000\r\nTransfer-Encoding: chunked\r\n\r\n'

# print(transfer_encoding_parser(raw_request))

def make_request(**request_param):  
    """ GET & POST only \n
    request_param for making a custom http requests or response\n
    Type: response or request\n
    Route: use for request only\n
    Status_code\n
    Host\n
    Content_Type\n
    Content_Length\n
    Connection: keep-alive\n
    Content\n
    Method: POST or GET\n
    Some http headers are automatically set but can be set manually as parameters\n
    You can add custom http headers headers if needed \n
    """

    version = "HTTP/1.1"
    # r = ""
    # host = request_param.get("Host")
    # content_type = request_param.get("Content_Type")
    content = ["" if request_param.get("Content") == None else request_param.get("Content")][0]
    print(request_param)
    if not (isinstance(content, bytes)): 
        content = content.encode()
    r_type = request_param.get("Type") # http type 
    connection = [" keep-alive" if request_param.get("Connection") == None else request_param.get("Connection")][0]
    method = request_param.get("Method")
    if request_param.get("Status_code"): status_code = int(request_param.get("Status_code"))
    else: status_code = None
     # request_param to skip for custom headers
    default_request_param = ["Route", "Host", "Content_Length", "Content_Type",  "Content", "Type", "Connection", "Method", "Status_code"]
    route = request_param.get('Route')
    # Prepare headers
    headers = {  
        "Connection": connection,
        "Host" if request_param.get("Host") != None else "": request_param.get("Host") if request_param.get("Host") != None else "",
        "Content-Type" if r_type == "Response" else "" : request_param.get("Content_Type") if r_type == "Response" and request_param.get("Content_Type") else "" ,
        "Content-Length" if len(content) != 0 else "": " "+ str(len(content)) if r_type == "Response" and content!=None else 0,
    }  
    # Prepare custom headers can have duplicate values which will be represented as a list
    for key, value in request_param.items():
        if not (key in default_request_param):
            headers[key] = value

    status_code_dictionary = {
        200: " OK",
        400: " Bad Request",
        301: " Moved Permanently",
        302: " Temporary Redirect",
        404: " Not Found", 
        410: " Gone",
        500: " Internal Server Error",
        503: " Service Unavailable",
        505: " Version Not Supported",
        303: " See Other", 
    }

    # Add status line with headers
    if r_type.lower() == "response":
        status_line = f"{version} {status_code}"
        # if status_code == 200: status_line = status_line+" OK"
        if status_code_dictionary.get(status_code): status_line = status_line+status_code_dictionary.get(status_code)
        else: status_line = status_line + " Internal Server Error"
    if r_type.lower() == "request": status_line = f"{method} {route} {version}"
    if content == None: content=b""
    print(content.decode())
    return status_line.encode()+b"\n"+process_json(headers).encode()+b"\n"+content


def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return "200", file.read()
    except FileNotFoundError:
        return "404 FILE NOT FOUND"

def merge(dict1, dict2):
    return(dict2.update(dict1))

def readb(file_path):
    try:
        with open(file_path, "rb") as file:
            return "200", file.read()
    except:  
        return ("FILE NOT FOUND", "404")
    
static_routes = []

# Return status code template bytes data and file type
def render_template(file_path, content_type = "text/html"):
    status_code, template_data = read_file(file_path)

    # # Create routes for css, js and images
    html_parser = BeautifulSoup(template_data, 'html.parser')
    tag_list = [html_parser.find_all("link"), html_parser.find_all("script"), html_parser.find_all("img")]
    for tags in tag_list:
        for tag in tags:
            static_routes.append(tag.get("src"))  # Route, function to retrieve data
            

    return template_data, status_code, content_type

# render_template("templates/index.html")

# Return Status code static bytes data and file type
def static_file(file_name, static_folder):
    try:
        with open(f"{static_folder}/{file_name}", "rb") as file:
            return (file.read(), 200, file_type(file_name), "")  # Data, status_code, content_type
    except FileNotFoundError:
        return (f"404 File Not Found {static_folder}/{file_name}", 404, "text/plain", "")


# Blueprint for import routes to other files  
class Blueprints():
    def __init__(self):
        self.routes = {}

    def route(self, route):   # Decorator function
        def process_routes(func): # wrapper function
            self.routes[route] = func  # Store the routes for future use
        return process_routes  # run wrapper function

def get_host_parser(web_addr):  # Return host "www.example.com" from "http://192.168.1.194:5000/www.example.com/home-page.html"
    if "http" in web_addr and not ("https" in web_addr): web_addr = web_addr[7:len(web_addr)]
    elif "https" in web_addr: web_addr = web_addr[8:len(web_addr)]
    if "/" in web_addr: return web_addr.split("/")[1]
    return None

# print(get_host_parser("http://192.168.1.194:5000/wweeew.exaaample.com/home-page.html/aaa"))
# print(get_host_parser("https://192.168.1.194:5000/www.a.com/home-page.html/Hell.com"))
# print(get_host_parser("/google.com"))

def process_endPoint_path(end_point):
    split_end_point = end_point.split("/")[2:]
    if split_end_point == [""] or split_end_point == []: return "/"
    [split_end_point.pop(i) if split_end_point[i] == "" else None for i in range(len(split_end_point))]
    
    return "".join([f"/{split_end_point[i]}"  for i in range(len(split_end_point))])

# print(process_endPoint_path("/www.google.com/abac/HelloWorld.html"))  # --->   "/abac/HelloWorld.html/"


def unicode_decoder(data):
    return "".join([chr(list(data)[i]) for i in range(len(data))])

    # Connect to web server on port 443 with ssl  
def connect_to_target(TARGET_HOST, TARGET_PORT):
    if ":" in TARGET_HOST: TARGET_HOST, TARGET_PORT = TARGET_HOST.split(":")[0], int(TARGET_HOST.split(":")[1])
    conn_target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_target.connect((TARGET_HOST, TARGET_PORT))
    print(f"Connected to target: {TARGET_HOST}:{TARGET_PORT}")
    if TARGET_PORT == 443: conn_target = ssl.create_default_context().wrap_socket(sock=conn_target, server_hostname=TARGET_HOST)
    return conn_target



# raw_response_data = """HTTP/1.0 400 Bad Request
# Content-Type: text/html; charset=UTF-8
# Referrer-Policy: no-referrer
# Content-Length: 1555
# Date: Sun, 01 Oct 2023 03:57:30 GMT

# <!DOCTYPE html>
# <html lang=en>
#   <meta charset=utf-8>
#   <meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width">
#   <title>Error 400 (Bad Request)!!1</title>
#   <style>
#     *{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_1</style>"""

# raw_request_data = """GET /path/to/resource HTTP/1.1
# Host: www.example.com

# Hello  abc
# World
# """

# response_data = parser(raw_request_data)
# print(response_data[4])

# print()
# response_data = parser(raw_response_data)
# print(response_data[4])

# # Set parameters for the request
# request_params = {
#     "Type": "Request",
#     "Method": "GET",
#     "Host": "example.com",
#     "Route": "/api/resource",
# }

# response_params = {  # Payload with
#     "Type": "Response",
#     "Status_code": "200",
#     "Host": "",
#     "Content_Type": "text/plain",
#     "Body": "HelloWorld",
#     "X-Custom-Header": "Custom Value",
#     }

# copy = ""

# # data = {"Host": "example.com", "": "", "Content-Length": 0, "Route": "/api/resource"}
# # process_json(data)

# Make the request
# response = make_request(**request_params)

# print(response)


# print("\n")
# Set parameters for the response
# response_params = {  # Payload with
#     "Type": "Response",
#     "Status_code": 200,
#     "Host": "example.com",
#     "Content_Type": "text/plain",
#     "Body": "You have been hack retard!",
#     "X-Custom-Header": "Custom Value",
#     "Custom-Header2": "Hello World"
# }

# # Make the response
# response = make_request(**response_params)
# print(response.decode())

# print(response)
# print("\n")

# response_dict = parser(response)

# print(response_dict)


# a = """POST /api/endpoint HTTP/1.1
# Host: example.com
# Content-Type: application/json
# Content-Length: 36

# {"name":"John","age":30}
# """

# b = parser(a)

# print(b)