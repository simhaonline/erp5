## Script (Python) "folder_delete"
##title=Delete objects from a folder
##parameters=form_id='',selection_index=None,object_uid=None,selection_name=None,field_id=None,uids=None,cancel_url=''

#return 'uids: %s, ids: %s' % (str(uids),str(ids))
#return form_from

REQUEST=context.REQUEST
qs = ''
ret_url = ''

if REQUEST.has_key('ids') and (len(REQUEST['ids'])>0):
  ret_url = context.absolute_url() + '/' + form_id
  context.manage_delObjects(ids=REQUEST['ids'], REQUEST=REQUEST)
  qs = '?portal_status_message=Deleted.'
elif REQUEST.has_key('uids') and (len(REQUEST['uids'])>0):
  ret_url = context.absolute_url() + '/' + form_id
  context.manage_delObjects(uids=REQUEST['uids'], REQUEST=REQUEST)
  qs = '?portal_status_message=Deleted.'
# This is the case when we used the folder_delete_view page
elif uids is not None:
  ret_url=cancel_url
  context.manage_delObjects(uids=uids, REQUEST=REQUEST)
  qs = '?portal_status_message=Deleted.'
else:
  qs = '?portal_status_message=Please+select+one+or+more+items+first.'

return REQUEST.RESPONSE.redirect( ret_url + qs )
