##parameters=form_id, field_id, selection_index, selection_name, uids, object_uid

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST

o = context.portal_catalog.getObject(object_uid)

if o is None:
  return "Sorrry, Error, the calling object was not catalogued. Do not know how to do ?"

form = getattr(context, form_id)
field = form.get_field(field_id)
base_category = field.get_value('base_category')
portal_type = map(lambda x:x[0],field.get_value('portal_type'))

if uids:
  # Clear the relation
  o.setValueUids(base_category,  (), portal_type=portal_type)
  # Warning, portal type is at strange value because of form
  # And update it
  o.setValueUids(base_category, uids, portal_type=portal_type)
else:
  # Clear the relation
  o.setValueUids(base_category,  (), portal_type=portal_type)

if not selection_index:
  redirect_url = '%s/%s?%s' % ( o.absolute_url()
                            , form_id
                            , 'portal_status_message=Data+Updated.'
                            )
else:
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( o.absolute_url()
                            , form_id
                            , selection_index
                            , selection_name
                            , 'portal_status_message=Data+Updated.'
                            )


request[ 'RESPONSE' ].redirect( redirect_url )
