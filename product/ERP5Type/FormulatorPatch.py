##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.Formulator.Field import Field

class PatchedField:

    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_key(self, validation=0, key=None):
        """Generate the key Silva uses to render the field in the form.
        """
        # Patched by JPS for ERP5 in order to
        # dynamically change the name
        if key is not None:
          return 'field_%s' % key
        if self.field_record is None:
            return 'field_%s' % self.id
        elif validation:
            return self.id
        elif isinstance(self.widget, MultiItemsWidget):
            return "%s.%s:record:list" % (self.field_record, self.id)
        else:
            return '%s.%s:record' % (self.field_record, self.id)

    security.declareProtected('View', 'render')
    def render(self, value=None, REQUEST=None, key=None):
        """Render the field widget.
        value -- the value the field should have (for instance
                 from validation).
        REQUEST -- REQUEST can contain raw (unvalidated) field
                 information. If value is None, REQUEST is searched
                 for this value.
        if value and REQUEST are both None, the 'default' property of
        the field will be used for the value.
        """
        return self._render_helper(self.generate_field_key(key=key), value, REQUEST)

Field.generate_field_key = PatchedField.generate_field_key
Field.render = PatchedField.render

from Products.Formulator.Validator import SelectionValidator

class PatchedSelectionValidator(SelectionValidator):

    def validate(self, field, key, REQUEST):
        value = StringBaseValidator.validate(self, field, key, REQUEST)

        if value == "" and not field.get_value('required'):
            return value

        # get the text and the value from the list of items
        # Patch by JPS for Listbox cell
        for item in field.get_value('items', cell=getattr(REQUEST,'cell',None)):
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item

            # check if the value is equal to the string/unicode version of
            # item_value; if that's the case, we can return the *original*
            # value in the list (not the submitted value). This way, integers
            # will remain integers.
            # XXX it is impossible with the UI currently to fill in unicode
            # items, but it's possible to do it with the TALES tab
            if field.get_value('unicode') and type(item_value) == type(u''):
                str_value = item_value.encode(field.get_form_encoding())
            else:
                str_value = str(item_value)

            if str_value == value:
                return item_value

        # if we didn't find the value, return error
        self.raise_error('unknown_selection', field)

SelectionValidator.validate = PatchedSelectionValidator.validate

from Products.Formulator.Validator import MultiSelectionValidator

class PatchedMultiSelectionValidator(MultiSelectionValidator):

    def validate(self, field, key, REQUEST):
        values = REQUEST.get(key, [])
        # NOTE: a hack to deal with single item selections
        if type(values) is not type([]):
            # put whatever we got in a list
            values = [values]
        # if we selected nothing and entry is required, give error, otherwise
        # give entry list
        if len(values) == 0:
            if field.get_value('required'):
                self.raise_error('required_not_found', field)
            else:
                return values
        # convert everything to unicode if necessary
        if field.get_value('unicode'):
            values = [unicode(value, field.get_form_encoding())
                      for value in values]

        # create a dictionary of possible values
        value_dict = {}
        for item in field.get_value('items', cell=getattr(REQUEST,'cell',None)): # Patch by JPS for Listbox
            try:
                item_text, item_value = item
            except ValueError:
                item_text = item
                item_value = item
            value_dict[item_value] = 0

        # check whether all values are in dictionary
        result = []
        for value in values:
            # FIXME: hack to accept int values as well
            try:
                int_value = int(value)
            except ValueError:
                int_value = None
            if int_value is not None and value_dict.has_key(int_value):
                result.append(int_value)
                continue
            if value_dict.has_key(value):
                result.append(value)
                continue
            self.raise_error('unknown_selection', field)
        # everything checks out
        return result

MultiSelectionValidator.validate = PatchedMultiSelectionValidator.validate