#!/usr/bin/env python
#===============================================================================
# This file is part of PyManageMC.
#
#    PyManageMC is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    PyManageMC is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyManageMC.  If not, see http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#===============================================================================
import os
import sys

if __name__ == "__main__":
    import os, sys

    # Calculate the path based on the location of the WSGI script.
    settingsdir = os.path.dirname(__file__)
    project = os.path.dirname(settingsdir)
    sys.path.append(project)
    sys.path.append('/usr/lib/python2.7/site-packages')
    sys.path.append('/usr/local/lib/python2.7/dist-packages')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manageMC.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
