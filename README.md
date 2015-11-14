# pypartypix
Html slideshow that allows new pictures to be inserted from guests through a webclient.
pypartypix is a simple python (3) server which allows clients to upload images through a simple web interface.
The slideshow.html file can be startet local and will display all images in the index.txt file.
Index.txt gets generated from the server.

New images will be next in the slideshow. There are quite a few settings for the slideshow, move the mouse to the upper part of the slideshow to adjust them.

As a simple security measure a uuid can be used to disallow unwanted users.
This service runs unencrypted because a self signed certificate whould be a pain for the users.

As a security measure this server should run in a chroot or otherwide unprivileged environment.

This was meant as a poc to demonstrate that client for such an app is not necessary.

The option --help displays a help.

LICESNE:
MIT

CREDITS:
Thanks to the developer of Party Pix! for the idea, the client is Android only and the server is Java and seems to be closed source.

Vegas:
http://vegas.jaysalvat.com/

Jquery:
https://jquery.com/
