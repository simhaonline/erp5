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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

class PaySheet(XMLObject):
    """
    A paysheet will store data about the salary of an employee
    """

    meta_type = 'ERP5 Pay Sheet'
    portal_type = 'Pay Sheet'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View) 

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
# no motion	      , PropertySheet.Arrow
                      , PropertySheet.PaySheet
                      )

    # Declarative Interface

    # Factory Type Information
    factory_type_information = \
        {  'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : ''
         , 'icon'           : 'document_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addPaySheet'
         , 'immediate_view' : 'pay_sheet_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'action'        : 'pay_sheet_view'
          , 'category'      : 'object_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'action'        : 'pay_sheet_print'
          , 'category'      : 'object_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'action'        : 'metadata_edit_form'
          , 'category'      : 'object_view'
          , 'permissions'   : (
              Permissions.ModifyPortalContent, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'action'        : 'translation_template'
          , 'category'      : 'object_action'
          , 'permissions'   : (
              Permissions.View, )
          }
        )
        }

        
