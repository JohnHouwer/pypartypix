pypartypix a picture upload server for html slideshows 
======================================================
Allows guests to upload pictures through a simple webinterface.
The picture is inserted as the next slide in the slideshow.

----

Html slideshow that allows new pictures to be inserted from guests through a webclient.
pypartypix is a simple python (3) server which allows clients to upload images through a simple web interface.
The slideshow.html file can be startet local and will display all images in the index.txt file.
Index.txt gets generated from the server.

New images will be next in the slideshow. There are quite a few settings for the slideshow, move the mouse to the upper part of the slideshow to adjust them.

As a simple security measure a uuid can be used to disallow unwanted users.
This service runs unencrypted because a self signed certificate whould be a pain for the users.

As a security measure this server should run in a chroot or otherwide unprivileged environment.

This was meant as a poc to demonstrate that client for such an app is not necessary.


Usage
-----

% python3 -m pypartypix -h
or
% ./pyparty -h 
usage: pyparty [-h] [-p PORT] [-g] [-u UUID] [-d DIR] [-i FILE] [-q [FILE]]
               [-s SCALE] [-H HOST] [-r] [-w]

Image Upload Server

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port the server should listen to
  -g, --genuuid         Generate UUID used for authorization
  -u UUID, --uuid UUID  use UUID
  -d DIR, --directory DIR
                        DIR used for image storage
  -i FILE, --index FILE
                        File used for index storage. The slideshow needs to
                        read this file
  -q [FILE], --qrcode [FILE]
                        File used for qrcode storage
  -s SCALE, --qrscale SCALE
                        Scale used for qrcode
  -H HOST, --host HOST  Hostname used for URL/QRCODE
  -r, --run             Don't start the server
  -w, --web             Autostart Webbrowser


LICENSE
-------
MIT


CREDITS
-------
Thanks to the developer of Party Pix! for the idea, hist client is Android only and the server is Java and seems to be closed source.

Python:
https://python.org

Vegas:
http://vegas.jaysalvat.com/

Jquery:
https://jquery.com/
