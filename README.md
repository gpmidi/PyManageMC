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


Known Issues
============

Branch: dockerBased
--------------
This is the current dev branch as it's being moved over to a docker-based
setup.

See [the PyManageMC Open Issues](https://github.com/gpmidi/PyManageMC/issues) page.


Branch: master
--------------
This branch has the previous manual tracking section. It does not have working
management.


Branch: released
--------------
None yet since this project is still alpha...


Long Term TODOs & Ideas
===============
* Add support for managing Minecraft servers on multiple machines from a single web UI
* Add support for managing Minecraft servers that run as different users than the "default" Celery daemon
* A minimal, automatic backup system (Low priority as external software can do a better job)
* Support for working with common backup utilities. This includes:
  * Easy to use scripts that can be run to disable save-all before the backup starts and then re-enable save-all once the backup is complete.
  * A timeout on backups save-all in case the backup tool fails to call the 'all done' script that re-enables save-all.
  * LVM-based COW snapshot support
* Add support for using git to track changes to a given server's map. It should support local-only repos at the very least. If reasonable, add remote repo support too.


License
=======

PyManageMC: GPLv2
Bootstrap: Apache License v2.0
Dajax(ice): FIXME
jQuery: FIXME