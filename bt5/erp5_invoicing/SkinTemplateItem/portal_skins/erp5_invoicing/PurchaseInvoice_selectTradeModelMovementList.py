kw['parent_specialise_portal_type'] = 'Trade Model Simulation Rule'
kw['explanation_portal_type'] = ('Purchase Order', 'Purchase Packing List', 'Returned Purchase Packing List',
                                       'Purchase Invoice Transaction', 'Purchase Invoice')
kw['grand_parent_simulation_state'] = 'started', 'stopped', 'delivered', 'confirmed'
kw['portal_type'] = 'Simulation Movement'

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

return context.portal_catalog(**kw)
