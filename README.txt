============
Assembly CMS
============

This is the Assembly CMS. It was created to replace Plone as the web content
management system for the Assembly (and related) websites and started during
Assembly Summer 2009. It is based on Zope/Grok.

Goal and vision
---------------

The Assembly CMS is intended to be a CMS with a small and simple but flexible
core. It is intended to be able to serve different specialised purposes on a
single content model. The main goal are public web sites.

It is intended to:

- be easy to work with for smart but occasional users
- run multiple sites within a single server
- easily create and maintain custom public layouts
- easily create content extensions like workflow or multi-lingual content
- be easy to test

Getting started
---------------

Assuming that Python 2.5 is already installed on your system you can install
the CMS from this checkout by applying the following steps::

    $ cp buildout.cfg.example buildout.cfg
    $ python2.5 bootstrap.py
    $ bin/buildout

The last buildout call might take a few minutes depending on your network
connection.

You can then run the CMS by calling the init script::

    $ ./etc/init.d/asm.cms-zeo start
    $ ./etc/init.d/asm.cms-server start

The server is now accessible from a browser by opening the URL::

    http://localhost:8080/

This will open grok's application management screen which requires you to log
in. If you used the example buildout configuration then the username is
'admin' and the password is 'admin' as well.

After logging in you can create a new CMS site by adding an application of
type `asm.cms.cms.CMS`, giving it a name and pressing 'Create'.

The new site will be shown in the listing where you can now click the name to
visit the CMS user interface.

To stop the CMS server, you can call the init script again::

    $ ./etc/init.d/asm.cms-server stop

License note
------------

The CMS core and the general extensions are licensed under ZPL 2.1. The skin
included in this repository has a proprietary license and is only included for
educational purposes. You are not allowed to create derived works from the
skin or run it as a website!
