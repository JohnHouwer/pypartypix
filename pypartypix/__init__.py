#!/usr/bin/python3

import argparse
import glob
import http.server
import os
import re
import socketserver
import uuid
import time
#import pyparty
import pkg_resources
import webbrowser

# print(pkg_resources.resource_listdir('pyparty', ''))

def drop_resource(name=""):
    for n in name:
        print(n)
        s = pkg_resources.resource_string('pypartypix', n)
        with open(n, 'wb') as f:
            f.write(s)

# if __name__ == '__main__':
if True:

    parser = argparse.ArgumentParser(description='Image Upload Server')
    parser.add_argument('-p', '--port', metavar='PORT', type=int,
                        help='Port the server should listen to',
                        default="8000", dest="port")
    parser.add_argument('-g', '--genuuid',  action='store_true', dest="genuuid",
                        help='Generate UUID used for authorization')
    parser.add_argument('-u', '--uuid', metavar="UUID", type=str, dest="uuid",
                        help="use UUID")
    parser.add_argument('-d', '--directory', metavar="DIR", type=str,
                        dest="directory", help="DIR used for image storage",
                        default="images")
    parser.add_argument('-i', '--index', metavar="FILE", type=str, dest="index",
                        help="File used for index storage. "
                        + "The slideshow needs to read this file",
                        default="index.txt")
    parser.add_argument('-q', '--qrcode', metavar="FILE", type=str,
                        dest="qrcode", const="pyparty_server_url_qr",
                        nargs='?', help="File used for qrcode storage")
    parser.add_argument('-s', '--qrscale', metavar="SCALE", type=int,
                        dest="qrscale", default=8,
                        help="Scale used for qrcode")
    parser.add_argument('-H', '--host', metavar="HOST", type=str,
                        dest="host", default=http.server.socket.gethostname(),
                        help="Hostname used for URL/QRCODE")
    parser.add_argument('-r', '--run', action='store_true',
                        dest="run", 
                        help="Don't start the server")

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
                    if os.path.isfile(fn):
                        fn = "{}_{}".format(str(time.time()), fn)
                    with open(fn, 'wb') as f:
                        f.write(post_body)

                    with open(args.index, "a") as idx:
                        idx.write(fn + "\n")
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
    try:
        os.mkdir(args.directory + "/vegas")
    except:
        pass
    os.chdir(args.directory)

    print("Create index from file in '{}'".format(args.directory))
    
    with open(args.index, "w") as idx:
        for f in glob.glob("*"):
            if re.search("\.((jpe?g)|(png)|(gif))", f.lower()) is not None:
                idx.write(f + "\n")

    drop_resource( name=[ 'vegas/vegas.js', 'vegas/vegas.css', 'slideshow.html', 'jquery-latest.min.js', ],) 
    print("serving at port", args.port)

    server_url = "http://{}:{}/{}".format(args.host, args.port, rstr)

    print("\n", "Clients can use the following URL to post pictures:\n\n",
          server_url, "\n" * 3)

    if args.qrcode:
        try:
            import pyqrcode
            server_url_qr = pyqrcode.create(server_url, error='H')
            print(server_url_qr.terminal(module_color='black', background='white',
                  quiet_zone=1))
            server_url_qr.svg(args.qrcode + ".svg", scale=args.qrscale)
            server_url_qr.png(args.qrcode + ".png", scale=args.qrscale,
                              module_color=[0, 0, 0, 255],
                              background=[0xff, 0xff, 0xff])
        except Exception as e:
            print("Could not import/use 'pyqrcode' it can be installed with",
                  "\n 'pip3 install pyqrcode' \nand  \n 'pip3 install pypng'\n")
    print("starting webbrowser")
    webbrowser.open("slideshow.html")
    print("Exit server with ctrl + c")
    try:
        if not args.run:
            httpd.serve_forever()
    except KeyboardInterrupt as e:
        exit(0)
