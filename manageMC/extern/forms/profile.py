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
''' User profile forms
Created on Jan 12, 2013

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
from django import forms
from extern.models import *

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # @UndefinedVariable
        exclude = (
                   'user',
                   )
        fields = (
                  'screenname',
                  'first_name',
                  'last_name',
                  'publicName',
                  'miscContactInfo',
                  )
    first_name = forms.CharField(
                                 max_length = 255,
                                 min_length = 0,
                                 required = False,
                                 label = "First Name",
                                 help_text = "Your first name - Only visible to Admins - Optional",
                                 )
        
    last_name = forms.CharField(
                                 max_length = 255,
                                 min_length = 0,
                                 required = False,
                                 label = "Last Name",
                                 help_text = "Your last name - Only visible to Admins - Optional",
                                 )

#    email = forms.EmailField(
#                             max_length = 75,
#                             min_length = 0,
#                             required = False,
#                             label = "Email Address",
#                             help_text = "Your email address",
#                             )
