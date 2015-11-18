#!/usr/bin/python3

import argparse
import glob
import http.server
import os
import re
import socketserver
import uuid

parser = argparse.ArgumentParser(description='Image Upload Server')
parser.add_argument('-p', '--port', metavar='PORT', type=int,
                    help='Port the server should listen to',
                    default="8000", dest="port")
parser.add_argument('-g', '--genuuid',  action='store_true', dest="genuuid",
                    help='generate UUID used for authorization')
parser.add_argument('-u', '--uuid', metavar="UUID", type=str, dest="uuid",
                    help="use UUID")
parser.add_argument('-d', '--directory', metavar="DIR", type=str,
                    dest="directory", help="DIR used for image storage",
                    default="images")
parser.add_argument('-i', '--index', metavar="FILE", type=str, dest="index",
                    help="File used for index storage. "
                    + "The slideshow needs to read this file.",
                    default="index.txt")

args = parser.parse_args()

if args.genuuid:
    rstr = uuid.uuid4()

if args.uuid:
    rstr = args.uuid

try:
    print("UUID is:", rstr)
except:
    print("NO UUID is set, Clients don't need a secret uri")
    rstr = ""


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
<button type="submit">Upload</button>
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
            fn = fn.replace(" ", "_").replace("/", "_")

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
                if os.path.isfile(args.directory + fn):
                    fn = "{}_{}".format(str(time.time()), fn)
                fnpath = "{}/{}".format(args.directory, fn)
                with open(fnpath, 'wb') as f:
                    f.write(post_body)

                with open(args.index, "a") as idx:
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

httpd = socketserver.TCPServer(("", args.port), CameraHTTPRequestHandler)

try:
    os.mkdir(args.directory)
except:
    print("Dir: '{}' already exists".format(args.directory))

print("Create Index from file in '{}'".format(args.directory))
with open(args.index, "w") as idx:
    for f in glob.glob(args.directory + "/*"):
        idx.write(f + "\n")

print("serving at port", args.port)

print("\n", "Clients can use the following URL to post pictures:\n\n",
      "http://{}:{}/{}".format(http.server.socket.gethostname(),
                               args.port, rstr), "\n" * 3)
httpd.serve_forever()
