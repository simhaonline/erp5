##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Globals import InitializeClass, Persistent, Acquisition
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions as ERP5Permissions
import string

from zLOG import LOG

class Selection(Acquisition.Implicit, Traversable, Persistent):
    """
        Selection

        A Selection instance allows a ListBox object to browse the data
        resulting from a method call such as an SQL Method Call. Selection
        instances are used to implement persistent selections in ERP5.

        Selection uses the following control variables

        - selection_method      --  a method which will be used
                                    to select objects

        - selection_params      --  a dictionnary of parameters to call the
                                    method with

        - selection_sort_on     --  a dictionnary of parameters to sort
                                    the selection

        - selection_uids        --  a list of object uids which defines the
                                    selection

        - selection_invert_mode --  defines the mode of the selection
                                    if mode is 1, then only show the
                                    ob

        - selection_list_url    --  the URL to go back to list mode

        - selection_checked_uids --  a list of uids checked

        - selection_domain_path --  the path to the root of the selection tree


        - selection_domain_list --  the relative path of the current selected domain

        - selection_report_path --  the report path

        - selection_report_list -- list of open report nodes

    """

    security = ClassSecurityInfo()

    def __init__(self, method_path=None, params={}, sort_on=[],
                 uids=[], invert_mode=0, list_url='',
                 columns=[], checked_uids=[]):
        self.selection_method_path = method_path
        self.selection_params = params
        self.selection_uids = uids
        self.selection_invert_mode = invert_mode
        self.selection_list_url = list_url
        self.selection_columns = columns
        self.selection_sort_on = sort_on
        self.selection_checked_uids = checked_uids
        self.selection_domain_path = ('portal_categories',)
        self.selection_domain_list = ((),)
        self.selection_report_path = ('portal_categories',)
        self.selection_report_list = ((),)

    def edit(self, params=None, **kw):
        if params is not None:
          self.selection_params = {}
          for key in params.keys():
            # We should only keep params which do not start with field_
            # in order to make sure we do not collect unwanted params
            # resulting form the REQUEST generated by an ERP5Form submit
            if key[0:6] != 'field_':
              self.selection_params[key] = params[key]
        if kw is not None:
          for k,v in kw.items():
            if v is not None:
              setattr(self, 'selection_%s' % k, v)

    def __call__(self, selection_method = None, context=None, REQUEST=None):
        if self.selection_invert_mode is 0:
          if selection_method is None:
            selection_method = context.unrestrictedTraverse(self.selection_method_path)
          if hasattr(self, 'selection_sort_on'):
            if len(self.selection_sort_on) > 0:
              new_sort_index = []
              for (k , v) in self.selection_sort_on:
                if v == 'descending' or v == 'reverse':
                  new_sort_index += ['%s DESC' % k]
                else:
                  new_sort_index += ['%s' % k]
              sort_order_string = string.join(new_sort_index,',')
              self.selection_params['sort_on'] = sort_order_string
            elif self.selection_params.has_key('sort_on'):
              del self.selection_params['sort_on']
          if selection_method is not None:
            if callable(selection_method):
              return selection_method(**self.selection_params)
            else:
              return []
          else:
            return []
        else:
          return context.portal_catalog(uid = self.selection_uids)

    def __getitem__(self, index, REQUEST=None):
        return self(REQUEST)[index]

    security.declareProtected(ERP5Permissions.View, 'getSelectionParams')
    def getSelectionParams(self):
        LOG('getSelectionParams',0,'selection_params: %s' % str(self.selection_params))
        if self.selection_params is None:
          self.selection_params = {}
        if type(self.selection_params) != type({}):
          self.selection_params = {}
        return self.selection_params

    def getSelectionListUrl(self):
        if self.selection_list_url is None:
          self.selection_list_url = ''
        return self.selection_list_url

    def getSelectionCheckedUids(self):
        if not hasattr(self, 'selection_checked_uids'):
          self.selection_checked_uids = []
        if self.selection_checked_uids is None:
          self.selection_checked_uids = []
        return self.selection_checked_uids

    def getSelectionDomainPath(self):
        if self.selection_domain_path is None:
          self.selection_domain_path = self.getSelectionDomainList()[0]
        return self.selection_domain_path

    def getSelectionDomainList(self):
        if self.selection_domain_list is None:
          self.selection_domain_list = (('portal_categories',),)
        return self.selection_domain_list

    def getSelectionReportPath(self):
        if self.selection_report_path is None:
          self.selection_report_path = ('portal_categories')
        return self.selection_report_path

    def getSelectionReportList(self):
        if self.selection_report_list is None:
          self.selection_report_list = (('portal_categories',),)
        return self.selection_report_list

