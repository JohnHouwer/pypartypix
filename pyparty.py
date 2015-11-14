#!/usr/bin/python3

import http.server
import socketserver
import sys
import re
import os
import glob
import uuid

# Default PORT
PORT = 8000

if "--port" in sys.argv:
    try:
        PORT = int(sys.argv[sys.argv.index("--port") + 1])
    except:
        print("Argument after --port is not valid")
        exit(255)

if "--genuuid" in sys.argv:
    rstr = str(uuid.uuid4())
if "--uuid" in sys.argv:
    rstr = sys.argv[sys.argv.index("--uuid") + 1]
if "--help" in sys.argv:
    print("""This software is under the MIT license.
    ./pyparty.py [--uuid <uuid>] [--genuuid] [--port <port>] [--help] \n
    --genuuid  # generates a new uuid
    --uuid <string> # gives a fixed uuid
    if no neither genuuid nor uuid is given, uuid check will be disabled
    --port <portnum> # controls the serverport
    --help # displays this help""")
    exit(0)

indexfile = "index.txt"
directory = "images"

try:
    print("UUID is:", rstr)
except:
    rstr = ""
    print("NO UUID is set, Clients don't need a secret uri")


class CameraHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    html = """
<!doctype html>
<html><head><title>Python Fast Picture Uploader</title>
<style>
input, button{
 background: lightsteelblue;
 font-size: 4vw;
 width: 95%;
 height: 45%;
 left: 2.5%;
 right: 2.5%;
 position:fixed;
}
input{top:2.5%;}
button{bottom:2.5%;}
</style>
</head>
<body>
<form enctype="multipart/form-data" method="POST">
<input name="picture" type="file" accept="image/*;capture=camera">
<button type="submit">Bild posten</button>
</form>
</body></html>
""".encode("utf-8")

    def check(self):
        if rstr != "":
            if self.path.strip("/") == str(rstr):
                ret = True
            else:
                ret = False
        else:
            ret = True
        return ret

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def denied(self):
        self.send_response(403)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            "Access Denied, please contact your host".encode("utf-8"))

    def accept(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self, **kwargs):
        if self.check():
            self.accept()
            self.wfile.write(self.html)
        else:
            self.denied()

    def do_POST(self):
        if self.check:
            con_len = int(self.headers.get('content-length', 0))
            boundary = self.headers.get_boundary()
            line = self.rfile.readline()
            con_len -= len(line)
            line = self.rfile.readline()

            # Get Filename from Request
            fn = re.findall(
                r'Content-Disposition.*name="picture"; filename="(.*)"',
                line.decode("utf-8"))[0]
            fn = fn.replace(" ", "_")

            if not fn:
                return (False, "Can't find out file name...")
            con_len -= len(line)
            line = self.rfile.readline()
            con_len -= len(line)
            preline = self.rfile.readline()
            con_len -= len(line)
            post_body = self.rfile.read(con_len)

            # Write File
            if re.search("\.((jpe?g)|(png)|(gif))", fn.lower()) is not None:
                if os.path.isfile(directory + fn):
                    fn = "{}_{}".format(str(time.time()), fn)
                fnpath = "{}/{}".format(directory, fn)
                with open(fnpath, 'wb') as f:
                    f.write(post_body)

                with open(indexfile, "a") as idx:
                    idx.write(fnpath + "\n")
            else:
                print("WRONG FILE TYPE")
            self.accept()
            self.wfile.write("""<!doctype html><html><head></head>
                            <body><a href="" style="font-size:4vw;">
                            Transfer complete. Upload next</a>
                            </body></html>""".encode("utf-8"))
        else:
            self.denied()

httpd = socketserver.TCPServer(("", PORT), CameraHTTPRequestHandler)

try:
    os.mkdir(directory)
except:
    print("Dir: '{}' already exists".format(directory))

print("Create Index from file in '{}'".format(directory))
with open(indexfile, "w") as idx:
    for f in glob.glob(directory + "/*"):
        idx.write(f + "\n")

print("serving at port", PORT)

print("\n", "Clients can use the following URL to post pictures:\n\n",
      "http://{}:{}/{}".format(http.server.socket.gethostname(),
                               PORT, rstr), "\n" * 3)
httpd.serve_forever()
