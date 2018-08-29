# -*- coding: utf-8 -*-
from __future__ import unicode_literals


session_key_filters = 'filters'
session_key_thumbs_ids = 'thumbs_ids'

session_key_coll_ids_by_coll_filter = 'coll_ids_by_coll_filter' 
session_key_coll_ids_by_obj_filter = 'coll_ids_by_obj_filter'



''' filters '''
def get_metadata_filters(session):
    return session[session_key_filters] if (session_key_filters in session) else None 

def set_metadata_filters(session, filters):
    session[session_key_filters] = filters


def get_folder_metadata_filter(session, default):
    folder = default
    mf = get_metadata_filters(session)
    if mf is not None:
        if 'Folder' in mf:
            folder = mf['Folder']
    return folder
    




''' thumbs_ids '''
def get_thumbs_ids(session):
    return session[session_key_thumbs_ids] if (session_key_thumbs_ids in session) else {}

def set_thumbs_ids(session, thumbs_ids):
    session[session_key_thumbs_ids] = thumbs_ids

def delete_thumbs_ids(session):
    if (session_key_thumbs_ids in session):
        del session[session_key_thumbs_ids]
    
    
    
''' allowed_collection_ids '''
def get_coll_ids_by_coll_filter(session):
    return session[session_key_coll_ids_by_coll_filter] if (session_key_coll_ids_by_coll_filter in session) else None

def set_coll_ids_by_coll_filter(session, ids):
    session[session_key_coll_ids_by_coll_filter] = ids
    
def get_coll_ids_by_obj_filter(session):
    return session[session_key_coll_ids_by_obj_filter] if (session_key_coll_ids_by_obj_filter in session) else None

def set_coll_ids_by_obj_filter(session, ids):
    session[session_key_coll_ids_by_obj_filter] = ids    


def get_allowed_ids(session):
    
    coll_ids = get_coll_ids_by_coll_filter(session)
    coll_ids2 = get_coll_ids_by_obj_filter(session)
    
    if coll_ids is None:
        return coll_ids2
    
    if coll_ids2 is None:
        return coll_ids

    # Both filters are used, find the intersection     
 
    b3 = [val for val in coll_ids.keys() if val in coll_ids2.keys()]
 
    collids = {}
    for key in b3:
        collids[key] = coll_ids[key]
   
    return collids    
    

def format_filters(session):
    
    coll_filters = []
    obj_filters = []
    
    filters = get_metadata_filters(session)
    if filters is not None:
        for key in filters.keys():
            splitted = key.split('-')
            if ( len(splitted) == 3):
                obj = splitted[0] == 'obj'
                name = filters[key] 
                if splitted[1] == 'lk':
                    like = '{} is like {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(like)
                    else:
                        coll_filters.append(like)
        
                if splitted[1] == 'gt':
                    gt = '{} greater then {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(gt)
                    else:
                        coll_filters.append(gt)
                if splitted[1] == 'lt':
                    lt = '{} less then {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(lt)
                    else:
                        coll_filters.append(lt)
                if splitted[1] == 'eq':
                    eq = '{} equals {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(eq)
                    else:
                        coll_filters.append(eq)
                        
                if splitted[1] == 'be':
                    be = '{} before {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(be)
                    else:
                        coll_filters.append(be)   
                        
                if splitted[1] == 'af':
                    af = '{} after {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(af)
                    else:
                        coll_filters.append(af)
        
                if splitted[1] == 'on':
                    on = '{} on {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(on)
                    else:
                        coll_filters.append(on)
                        
                        
                if splitted[1] == 'tb':
                    be = '{} before {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(be)
                    else:
                        coll_filters.append(be)   
                        
                if splitted[1] == 'ta':
                    af = '{} after {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(af)
                    else:
                        coll_filters.append(af)
        
                if splitted[1] == 'ti':
                    on = '{} on {}'.format(splitted[2], name)
                    if obj:
                        obj_filters.append(on)
                    else:
                        coll_filters.append(on)                                                                       
    return coll_filters, obj_filters

    