PyManageMC
==========

A web UI for managing multiple Minecraft servers. 

This interface and associated back end code is still in an early alpha stage. As of 2013-02-17, 
it can perform basic management operations for one or more servers on a single host. The use of 
Celery (http://celeryproject.org/) allows the Minecraft daemons to run on a different server than
the front end web server and also allows different users to be used. This enables easy privilege
separation and allows the server load to be spread out among more than one server without
fragmenting the management of the servers. 



_Note: Initially this will be focused on the the parts of server management outside of running 
and modifying the actual daemon. The long term goal is to have a one stop platform for most 
aspects of Minecraft server management. Users requiring something that works -right now- should
look to Thue's RFWAdmin (https://github.com/Thue/rfwadmin)._ 

License: GPLv2


Items In Progress
=====
* Add basic management of server instances via an interactive Python console


Long Term TODOs
======
* Add support for managing Minecraft servers on multiple machines from a single web UI
* Add support for managing Minecraft servers that run as different users than the "default" Celery daemon


Short Term TODOs
======
* Add a web interface for managing server instances
* Make the Admins list box bigger in the form for the server instance Admins chooser
* 