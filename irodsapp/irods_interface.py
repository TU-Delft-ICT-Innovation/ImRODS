from anytree import Node

import os.path
from irods.models import Collection, DataObject, DataObjectMeta, CollectionMeta, User as IrodsUser
from .models import Thumbnail, Folder, UserIrodsMetaDataAttribute
from datetime import date
from django.contrib.auth.models import User
from irods.query import SpecificQuery
import time
from wand.image import Image
from irods.exception import CAT_NO_ROWS_FOUND

from io import BytesIO   
import base64

from irodsapp.turodssession import TuRODSSession
from irodsapp.util import log_and_raise_exception, log_exception


def remove_none(attribute_name):
          
    with TuRODSSession() as session:

        sql = "select meta_attr_value from R_META_MAIN where meta_attr_name = '{}'".format(attribute_name)
        
        alias = 'remove_none'
        columns = [CollectionMeta.value]

        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        exception = None
        
        try:
            for result in query.get_results():
                print("Result: '{}'".format(result[CollectionMeta.value]))

        except Exception as e:
            exception = e
        # delete specific query
        _ = query.remove()
        
        if exception is not None:
            log_and_raise_exception('Error in remove_none', exception)

def get_collection_name(coll_id):
    with TuRODSSession() as session:
        query = session.query(Collection.name).filter(Collection.id == coll_id)
        result = query.execute()
        return result[0][Collection.name]
    return None

def get_collection_id(coll_name):
    with TuRODSSession() as session:
        query = session.query(Collection.id).filter(Collection.name == coll_name)
        result = query.execute()
        return result[0][Collection.id]
    return None

def get_size(irods_user):
    with TuRODSSession(irods_user) as session:
        query = session.query(DataObject.owner_name).count(DataObject.id).sum(DataObject.size)
        result = query.execute()
        return result[0][DataObject.size]
    return 0
  
def folders_recursive(coll, deep, folders):

    deep = deep + 1    
    
    if deep < 4:
        for col in coll.subcollections:
            folders.append({'display': col.path, 'value': col.path})
            folders_recursive(col, deep, folders)  
    
def folders(irods_user, root):
        
    folders = []
    
    for rt in root.split(';'):    
        folders.append({'display': rt, 'value': rt})
        with TuRODSSession(irods_user) as session:
            coll = session.collections.get(rt)
            folders_recursive(coll, 1, folders)
    return folders

def create_collection_clause(attr_name, attr_value):  
    
    clause = None
    att = attr_name[7:]
    
    if attr_name.startswith('col-gt-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as decimal) > {} and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('col-lt-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as decimal) < {} and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('col-eq-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as decimal) = {} and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)


    if attr_name.startswith('col-af-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as date) > '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('col-be-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as date) < '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('col-on-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as date) = '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
        
    if attr_name.startswith('col-ta-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as time) > '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)
    if attr_name.startswith('col-tb-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as time) < '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)
    if attr_name.startswith('col-to-'):
        clause = " AND cast (r_coll_meta_main.meta_attr_value as time) = '{}' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)        
        

    if attr_name.startswith('col-lk-'):
        clause = " AND r_coll_meta_main.meta_attr_value like '%{}%' and r_coll_meta_main.meta_attr_name = '{}' ".format(attr_value, att)

    return clause


def get_object_clauses(filters):
    clauses = []
    if filters is not None:
        for key in filters.keys():
            clause = create_obj_filter(key, filters[key])
            if clause != None:
                clauses.append(clause)
                
    nb_of_filters = len(clauses)
    if nb_of_filters == 0:
        return None
    else:
        return clauses
    
def get_collection_clauses(filters):
    clauses = []
    for key in filters.keys():
        clause = create_collection_clause(key, filters[key])
        if clause is not None:
            clauses.append(clause)
    
    nb_of_filters = len(clauses)
    if nb_of_filters == 0:
        return None
    else:
        return clauses


def get_irods_user_id(irods_user):
    try:
        with TuRODSSession() as session:
            query = session.query(IrodsUser.name, IrodsUser.id).filter(IrodsUser.name == irods_user)
            result = query.one()
            return result[IrodsUser.id]  
    except Exception as e:
        log_exception('Error in get_irods_user_id',e)

    return None


def set_filter(user, filters, starting_folder):
    
    object_clauses = get_object_clauses(filters)
    collection_clauses = get_collection_clauses(filters)
      
    coll_ids = None
    coll_ids2 = None

    if collection_clauses is not None:
        coll_ids = get_allowed_collections(collection_clauses, user, starting_folder)
               
    if object_clauses is not None:
        coll_ids2 = has_objects(object_clauses, user, starting_folder)

    return coll_ids2, coll_ids


def has_objects(clauses, user, starting_folder):
    
    coll_ids = {}
    
    irods_user_id = get_irods_user_id(user.profile.irods_user)
                
    with TuRODSSession() as session:

        base_sql = "select distinct R_DATA_MAIN.coll_id, R_COLL_MAIN.coll_name from R_DATA_MAIN " \
            "JOIN R_COLL_MAIN ON R_DATA_MAIN.coll_id = R_COLL_MAIN.coll_id " \
            "JOIN R_OBJT_METAMAP r_data_metamap ON R_DATA_MAIN.data_id = r_data_metamap.object_id " \
            "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
            "WHERE user_id in ( select group_user_id from R_user_group where user_id = {0})".format(irods_user_id)


        nb_of_filters = len(clauses)    
        columns = [DataObject.collection_id, DataObject.path]
                      
        if nb_of_filters == 1:
            sql = base_sql + clauses[0]
                                 
        else:
            sql = ''
            n = 0
            for clause in clauses:
                if n == 0:
                    sql = base_sql + clause
                    n = n + 1
                else:
                    sql = sql + ' intersect ' + base_sql + clause
        alias = 'list_data_name_idyy'
         
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None

        try:
            for result in query.get_results():
                collid = result[DataObject.collection_id]
                path = result[DataObject.path]
                for folder in starting_folder.split(';'):    
                    if path.startswith(folder):
                        coll_ids[path] = collid
                        break

        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e
        _ = query.remove()

        if exception is not None:
            log_and_raise_exception('Error in has_objects',exception)
    
    return coll_ids


def get_allowed_collections(clauses, user, starting_folder):
        
    coll_ids = {}

    irods_user_id = get_irods_user_id(user.profile.irods_user)
        
    with TuRODSSession() as session:

        base_sql = "select R_COLL_MAIN.coll_id, R_COLL_MAIN.coll_name, user_id from R_COLL_MAIN " \
                "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_COLL_MAIN.coll_id " \
                "JOIN R_OBJT_METAMAP r_coll_metamap ON R_COLL_MAIN.coll_id = r_coll_metamap.object_id " \
                "JOIN R_META_MAIN r_coll_meta_main ON r_coll_metamap.meta_id = r_coll_meta_main.meta_id " \
                "WHERE user_id in ( select group_user_id from R_user_group where user_id = {0})".format(irods_user_id)


        nb_of_filters = len(clauses)
        if nb_of_filters == 1:
            sql = base_sql + clauses[0]
                                 
        else:
            sql = ''
            n = 0
            for clause in clauses:
                if n == 0:
                    sql = base_sql + clause
                    n = n + 1
                else:
                    sql = sql + ' intersect ' + base_sql + clause
            

        alias = 'test_list_data_name_id15'
        columns = [Collection.id, Collection.name, Collection.map_id]

        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None
        try:
            for result in query.get_results():
                collid = result[Collection.id]
                collname = result[Collection.name]
                user_id = int(result[Collection.map_id])

                for folder in starting_folder.split(';'):
                    if collname.startswith(folder):
                        coll_ids[collname] = collid
                        break
        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e
        _ = query.remove()
        
        if exception is not None:
            log_and_raise_exception('Error in get_allowed_collections',exception)
    return coll_ids


def create_obj_filter(attr_name, attr_value):  
    
    clause = None
    att = attr_name[7:] #.strip()
    
    
    if attr_name.startswith('obj-gt-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as decimal) > {} and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('obj-lt-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as decimal) < {} and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('obj-eq-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as decimal) = {} and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)


    if attr_name.startswith('obj-af-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) > '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('obj-be-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) < '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)
    if attr_name.startswith('obj-on-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) = '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)

    if attr_name.startswith('obj-ta-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) > '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)
    if attr_name.startswith('obj-tb-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) < '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)
    if attr_name.startswith('obj-to-'):
        clause = " AND cast (r_data_meta_main.meta_attr_value as date) = '{}' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value + ":00", att)


    if attr_name.startswith('obj-lk-'):
        clause = " AND r_data_meta_main.meta_attr_value like '%{}%' and r_data_meta_main.meta_attr_name = '{}' ".format(attr_value, att)

    return clause


def get_distinct_metadata_attr():
    
    for usr in User.objects.all():
        profile = usr.profile    
        if profile is not None:
            irods_user = profile.irods_user
        
            irods_user_id = get_irods_user_id(irods_user)
            if irods_user_id is not None:
                get_distinct_collection_metadata_attr_per_user(usr, irods_user_id)
                get_distinct_object_metadata_attr_per_user( usr, irods_user_id)
            
def get_distinct_collection_metadata_attr_per_user(usr, irods_user_id):

    with TuRODSSession() as session:
        sql = "select distinct r_data_meta_main.meta_attr_name from R_COLL_MAIN " \
            "JOIN R_OBJT_METAMAP r_data_metamap ON R_COLL_MAIN.coll_id = r_data_metamap.object_id " \
            "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_COLL_MAIN.coll_id " \
            "where user_id in (select group_user_id from R_user_group where user_id = {0}) order by r_data_meta_main.meta_attr_name".format(irods_user_id)

        alias = 'get_distinct_collection_metadata_attr_per_user'
        columns = [CollectionMeta.name]
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None
        
        new_att_list = []

        try:
            for result in query.get_results():
                name = result[CollectionMeta.name]   
                name_unique = name.replace(' ', '%20')
                uima, created = UserIrodsMetaDataAttribute.objects.update_or_create(
                    name_unique__exact=name_unique, object_or_collection=False, user=usr)
                if created:
                    uima.name = name
                    uima.name_unique = name_unique
                    uima.save()
                    new_att_list.append(uima)
                    
                
 
        except Exception as e:
            exception = e

        # delete specific query
        _ = query.remove()

        if exception is not None:
            log_and_raise_exception("Error in get_distinct_collection_metadata_attr_per_user",exception)
        
    #for uima in UserIrodsMetaDataAttribute.objects.filter(user=usr, object_or_collection=False):
    for uima in new_att_list:
        uima.type = determine_collection_type(session, uima.name, irods_user_id)
        if uima.type is None:
            uima.delete()
        else:
            uima.save()
            
def is_date(value):
    is_a_date = True
    try:
        month, day, year = map(int, value.split("/"))
        date(year, month, day)
    except Exception:
        try:
            year, month, day = map(int, value.split("-"))
            date(year, month, day)
        except Exception:
            is_a_date = False
    return is_a_date

def is_time(value):
    is_a_time = True
    try:
        time.strptime(value.replace('\n', ''), '%H:%M:%S')
    except ValueError:
        is_a_time = False    
    return is_a_time   

def is_float(value):
    is_a_float = True
    try:
        float(value.replace('\n', ''))            
    except Exception:
        is_a_float = False
    return is_a_float

def determine_collection_type( session, attribute, irods_user_id):
    
    
    all_ints = True
    all_dates = True
    all_times = True
    no_rows = False
    
    sql = "select r_data_meta_main.meta_attr_value from R_COLL_MAIN " \
            "JOIN R_OBJT_METAMAP r_data_metamap ON R_COLL_MAIN.coll_id = r_data_metamap.object_id " \
            "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_COLL_MAIN.coll_id " \
            "where user_id in ( select group_user_id from R_user_group where user_id = {0}) and r_data_meta_main.meta_attr_name = '{1}'".format(irods_user_id, attribute)
                
    alias = 'determine_collection_type'
    columns = [CollectionMeta.value]
    query = SpecificQuery(session, sql, alias, columns)
    
    # register specific query in iCAT
    _ = query.register()
    
    exception = None
    
    try:
        for result in query.get_results():
            value = result[CollectionMeta.value]
            
            if all_ints:
                all_ints = is_float(value)
 
            if all_times:
                all_times = is_time(value)
                          
            if all_dates:
                all_dates = is_date(value)
                     
            if not all_ints and not all_dates and not all_times:
                break  
            
    except CAT_NO_ROWS_FOUND:
        no_rows = True
    except Exception as e:
        exception = e

    # delete specific query
    _ = query.remove()             

    if exception is not None:
        log_and_raise_exception("Error in determine_collection_type", exception)
        
    if no_rows:
        return None
    if all_ints:
        return 'De'
    if all_dates:
        return 'Da'
    if all_times:
        return 'Ti'
    return 'St'    

  
def get_distinct_object_metadata_attr_per_user(usr, irods_user_id):

    with TuRODSSession() as session:
        
        sql = "select distinct r_data_meta_main.meta_attr_name from R_DATA_MAIN " \
            "JOIN R_OBJT_METAMAP r_data_metamap ON R_DATA_MAIN.data_id = r_data_metamap.object_id " \
            "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
            "where user_id in ( select group_user_id from R_user_group where user_id = {0}) order by r_data_meta_main.meta_attr_name".format(irods_user_id)


        alias = 'list_data_name_id118'
        columns = [DataObjectMeta.name]
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        exception = None
        new_att_list = []
        try:
            for result in query.get_results():
                name = result[DataObjectMeta.name]
                name_unique = name.replace(' ', '%20')

                # if we have two attribute 'ColorMode' and 'ColorMode ' update_or_create does not see the difference @%$$%    
                uima, created = UserIrodsMetaDataAttribute.objects.update_or_create(
                    name_unique__exact=name_unique, object_or_collection=True, user=usr)
                if created:
                    uima.name = name
                    uima.name_unique = name_unique
                    uima.save()
                    new_att_list.append(uima)
                 
        except CAT_NO_ROWS_FOUND:
            pass                
        except Exception as e:
            exception = e

        # delete specific query
        _ = query.remove()
        
        if exception is not None:
            log_and_raise_exception('Error in get_distinct_object_metadata_attr_per_user', exception)
                
    #for uima in UserIrodsMetaDataAttribute.objects.filter(user=usr, object_or_collection=True):
    for uima in new_att_list:
        uima.type = determine_object_type(session, uima.name, irods_user_id)
        if uima.type is None:
            uima.delete()
        else:
            uima.save()


def determine_object_type( session, attribute, irods_user_id):
    
    
    all_ints = True
    all_dates = True 
    no_rows = False
    all_times = True
    
    sql = "select r_data_meta_main.meta_attr_value from R_DATA_MAIN " \
        "JOIN R_OBJT_METAMAP r_data_metamap ON R_DATA_MAIN.data_id = r_data_metamap.object_id " \
        "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
        "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
        "where user_id in ( select group_user_id from R_user_group where user_id = {0}) and r_data_meta_main.meta_attr_name = '{1}'".format(irods_user_id, attribute)


    alias = 'determine_object_type'
    columns = [DataObjectMeta.value]
    query = SpecificQuery(session, sql, alias, columns)
    
    # register specific query in iCAT
    _ = query.register()
    exception = None

    try:
        for result in query.get_results():
            value = result[DataObjectMeta.value]

            if all_ints:
                all_ints = is_float(value)

            if all_times:
                all_times = is_time(value)

            if all_dates:
                all_dates = is_date(value)
                    
            if not all_ints and not all_dates and not all_times:
                break  
    except CAT_NO_ROWS_FOUND:
        no_rows = True
                
    except Exception as e:
        exception = e


    # delete specific query
    _ = query.remove()           
    
    if exception is not None:
        log_and_raise_exception("Error in determine_object_type", exception)
        
    if no_rows:
        return None
    if all_ints:
        return 'De'
    if all_dates:
        return 'Da'
    if all_times:
        return 'Ti'
    return 'St'       


'''
    get a list of object ids ( so its also a list of thumbnails ids ) in the given folder and given filter
'''

def get_thumbnail_list_sql(filters, folder_start_with):
    
    clauses = []
    
    base_sql = "select distinct R_DATA_MAIN.data_id from R_DATA_MAIN " \
        "JOIN R_COLL_MAIN ON R_DATA_MAIN.coll_id = R_COLL_MAIN.coll_id " \
        "JOIN R_OBJT_METAMAP r_data_metamap ON R_DATA_MAIN.data_id = r_data_metamap.object_id " \
        "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
        "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id "
        
    if folder_start_with is None:    
        base_sql += "where R_DATA_MAIN.coll_id = {0} and user_id in ( select group_user_id from R_user_group where user_id = {1}) and (R_DATA_MAIN.data_name like '%.jpg' or R_DATA_MAIN.data_name like '%.tif' or R_DATA_MAIN.data_name like '%.jpeg')"
    else:
        base_sql += "where R_COLL_MAIN.coll_name like '{0}%' and user_id in ( select group_user_id from R_user_group where user_id = {1}) and (R_DATA_MAIN.data_name like '%.jpg' or R_DATA_MAIN.data_name like '%.tif' or R_DATA_MAIN.data_name like '%.jpeg')"
    
    if filters is not None:
        for key in filters.keys():
            clause = create_obj_filter(key, filters[key])
            if clause != None:
                clauses.append(clause)

    nb_of_filters = len(clauses)

         
    if nb_of_filters == 0:
        sql = "select distinct R_DATA_MAIN.data_id from R_DATA_MAIN " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
            "JOIN R_COLL_MAIN ON R_DATA_MAIN.coll_id = R_COLL_MAIN.coll_id " \
        
        if folder_start_with is None :
            sql  += "where R_DATA_MAIN.coll_id = {0} and user_id in ( select group_user_id from R_user_group where user_id = {1}) and (R_DATA_MAIN.data_name like '%.jpg' or R_DATA_MAIN.data_name like '%.tif' or R_DATA_MAIN.data_name like '%.jpeg')"    
        else:
            sql += "where R_COLL_MAIN.coll_name like '{0}%' and user_id in ( select group_user_id from R_user_group where user_id = {1}) and (R_DATA_MAIN.data_name like '%.jpg' or R_DATA_MAIN.data_name like '%.tif' or R_DATA_MAIN.data_name like '%.jpeg')"    
            
    elif nb_of_filters == 1:
        sql = base_sql + clauses[0]
                             
    else:
        sql = ''
        n = 0
        for clause in clauses:
            if n == 0:
                sql = base_sql + clause
                n = n + 1
            else:
                sql = sql + ' intersect ' + base_sql + clause
    return sql


def get_thumbnail_list(sql, thumbs_ids_collection):
    
    with TuRODSSession() as session:          
        columns = [DataObject.id]

        alias = 'get_thumbnail_list'
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()

        exception = None
        try:
            results = query.get_results()
            for result in results:
                object_id = result[DataObject.id]
                thumbs_ids_collection.append(object_id)

        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e

        # delete specific query
        _ = query.remove()
        
        if exception is not None:
            log_and_raise_exception("Error in get_thumbnail_list", exception)
        
    return thumbs_ids_collection


def search_objects(coll, parent, filters, irods_user_id):
    
    folder = coll.path
    
    clauses = []
    thumbs_ids_collection = []

    with TuRODSSession() as session:

        base_sql = "select R_DATA_MAIN.data_name, R_DATA_MAIN.data_id, R_DATA_MAIN.data_size from R_DATA_MAIN " \
            "JOIN R_OBJT_METAMAP r_data_metamap ON R_DATA_MAIN.data_id = r_data_metamap.object_id " \
            "JOIN R_META_MAIN r_data_meta_main ON r_data_metamap.meta_id = r_data_meta_main.meta_id " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
            "where R_DATA_MAIN.coll_id = {0} and user_id in (select group_user_id from R_user_group where user_id = {1})".format(coll.id, irods_user_id)


        if filters is not None:
            for key in filters.keys():
                clause = create_obj_filter(key, filters[key])
                if clause != None:
                    clauses.append(clause)

        nb_of_filters = len(clauses)

                
        columns = [DataObject.name, DataObject.id, DataObject.size]
                
        if nb_of_filters == 0:
            sql = "select R_DATA_MAIN.data_name, R_DATA_MAIN.data_id, R_DATA_MAIN.data_size from R_DATA_MAIN " \
            "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_DATA_MAIN.data_id " \
            "where R_DATA_MAIN.coll_id = {0} and user_id in (select group_user_id from R_user_group where user_id = {1})".format(coll.id, irods_user_id)

                      
        elif nb_of_filters == 1:
            sql = base_sql + clauses[0]
                                 
        else:
            sql = ''
            n = 0
            for clause in clauses:
                if n == 0:
                    sql = base_sql + clause
                    n = n + 1
                else:
                    sql = sql + ' intersect ' + base_sql + clause

        alias = 'xx_list_data_name_id11'
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        exception = None
        

        try:
            thumbs = []
            results = query.get_results()
            for result in results:
                name = result[DataObject.name]
                path = folder  + "/" + name
                id = result[DataObject.id]
                size = result[DataObject.size]         
         
                filename, extension = os.path.splitext(name)
                if is_thumbnail(extension):
                    thumbs.append(thumbs)
                    #th = Thumbnail.objects.filter(id=id).first()
                    #if th is not None:
                    thumbs_ids_collection.append(id)
                        
                Node(name, parent=parent, id=id, path=path, leaf=True, size=size)

        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e

        # delete specific query
        _ = query.remove()
        if exception is not None:
            log_and_raise_exception("Error in search_objects", exception)
        
    return thumbs_ids_collection


def is_allowed(coll_ids, coll_name):
    if coll_ids is None:
        return True
    else:
        s = str(coll_name)
        return s in coll_ids
    
def get_tree_root(node, irods_user, filters, allowed_collection_ids, root):

    ids = {}

    thumbs_ids_collection = None

    if allowed_collection_ids is not None:
        
        with TuRODSSession(irods_user) as session:
            coll = session.collections.get(node)
            my_root = Node(node, root, id=coll.id, path=node, expanded=False)

            for path in sorted(allowed_collection_ids.keys()):
                splitted = path.split(node)
                starting_root1 = node
                my_parent = my_root
                
                if len(splitted) == 2:
                    sub_folders = splitted[1][1:].split('/')
                    for x in range( len(sub_folders)):
                        p = starting_root1 + '/' + sub_folders[x]
                        
                        if p in ids:
                            my_parent = ids[p]
                        else:
                            try:
                                coll = session.collections.get(p)
                                my_parent = Node(p, my_parent, path=p, id=coll.id, expanded=False)
                                ids[p] = my_parent
                            except Exception as e:
                                print('Failed', e)
                                pass
                        starting_root1 = p

        return None, None

    irods_user_id = get_irods_user_id(irods_user)

    with TuRODSSession(irods_user) as session:
        try:
            coll = session.collections.get(node)
            
            if is_allowed(allowed_collection_ids, coll.path):
                sub = Node(node, root, id=coll.id, path=coll.path, expanded=False)
                thumbs_ids_collection = None
                #thumbs_ids_collection = search_objects(coll, sub, filters, irods_user_id)
                
                for col in coll.subcollections:
                    if is_allowed(allowed_collection_ids, col.path):
                        Node(col.name, sub, id=col.id, path=col.path)
            
            return thumbs_ids_collection, coll.id
        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            log_and_raise_exception("Error in get_tree_root", e)

    return thumbs_ids_collection, None

def get_tree(node, irods_user, filters, allowed_collection_ids):

    root = None
    thumbs_ids_collection = None

    irods_user_id = get_irods_user_id(irods_user)

    with TuRODSSession(irods_user) as session:
        try:
            coll = session.collections.get(node)
            
            if is_allowed(allowed_collection_ids, coll.path):
                root = Node(coll.name, id=coll.id,path=coll.path, expanded=False)
                thumbs_ids_collection = search_objects(coll, root, filters, irods_user_id)
                for col in coll.subcollections:
                    if is_allowed(allowed_collection_ids, col.path):
                        Node(col.name, root, id=col.id, path=col.path)
                        
            if root is None:
                return None, thumbs_ids_collection, coll.id
            
            
            return root, thumbs_ids_collection, coll.id
        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            log_and_raise_exception("Error in get_tree", e)
        
    return root, thumbs_ids_collection, None


def resize_picture_in_temp(obj, path):
    
    byte_io = None
    try:    
        with obj.open('r') as f:

            image_binary = f.read()
            with Image(blob=image_binary) as img:
                img.format = 'jpeg' 
                img.transform(resize='x400')
                byte_io = BytesIO()
                img.save(byte_io)
                
    except Exception as e:
        log_and_raise_exception("Error in resize_picture_in_temp on path {}".format(path), e)
    except:
        log_and_raise_exception("Error in resize_picture_in_temp on path {}".format(path), e)
    
    return byte_io
    


def is_thumbnail(extension):
    return (extension == ".jpg") or (extension == ".jpeg") or (extension == ".tif") or (extension == ".bmp")
'''

create_thumbnails_recursive:
    scan collection coll and create for eache jpeg, tiff or bmp a thumbnail if not already down
    save the thnumbail in the django model Thumbnail
    for each collection within this collection call this method
    
'''
def create_thumbnails_recursive(coll, lst):

    folder = Folder.objects.filter(id=coll.id).first()
    if folder is None:
        folder = Folder()
        folder.name = coll.path
        folder.id = coll.id
        folder.save()
    
    for obj in coll.data_objects:
        
        _, extension = os.path.splitext(obj.path)
        if is_thumbnail(extension):        
            t = Thumbnail.objects.filter(id=obj.id).first()
            if t is None:
                #create_thumbnail(obj, folder)
                lst.append({'path': obj.path, 'f_id': folder.id})
    for col in coll.subcollections:
        create_thumbnails_recursive(col, lst)


'''

create_thumbnails:
    start recursive scan all collections and create for eache jpeg, tiff or bmp a thumbnail if not already down
    
'''
        
def create_thumbnails():
    
    lst = []
    for usr in User.objects.all():
        profile = usr.profile
        
        if profile is not None:
                        
            if profile.create_thumbs is False:
                continue
            irods_user = profile.irods_user
            root = profile.root
            
            #root = '/tempZone/home/garys'

            with TuRODSSession(irods_user) as session:
                try:
                    coll = session.collections.get(root)
                    create_thumbnails_recursive(coll, lst)
                except Exception as e:
                    log_and_raise_exception("Error in create_thumbnails", e)

    '''
    placed the TuRODSSession in the loop: when the file for some reason is not available anymore ( bug iRods? )
    then a new connection would be made and the old one not be disconnected. By placing in the loop: after the with it will be closed!
    '''
    for entry in lst:
        file_data = None
        path = entry['path']
        folder_id = entry['f_id']
        with TuRODSSession(irods_user) as session:
            print('Creating thumb for ', path)
            obj = session.data_objects.get(path)
            file_data = resize_picture_in_temp(obj, path)
             
        if file_data is not None:
            t = Thumbnail()
            t.image = 'data:image/jpeg;base64,{}'.format(base64.b64encode(file_data.getvalue()).decode("ascii"))
            t.id = obj.id
            t.name = os.path.basename(obj.path)
            t.folder_id = folder_id
            t.save()             
    
    


def get_metadata(irods_user, path, folder):
    path = '/' + path
    data = {}

    with TuRODSSession(irods_user) as session:
            metadata = []
            if folder:
                obj = session.collections.get(path)
            else:
                obj = session.data_objects.get(path)

            for m in obj.metadata.items():
                d = { 'avu_id' : m.avu_id, 'key' : m.name, 'units' : m.units,  'val' : m.value}
                metadata.append(d)
                
            data['metadata'] = metadata

    sort_on = "key"
    decorated = [(dict_[sort_on], dict_) for dict_ in metadata]
    decorated.sort()
    result = [dict_ for (key, dict_) in decorated]
    data['metadata'] = result
    
    return data


def set_metadata(irods_user, dict, folder):
                
    path = dict['path']
    data = {}
    
    with TuRODSSession(irods_user) as session:
            if folder:
                obj = session.collections.get(path)
            else:
                obj = session.data_objects.get(path)
                
            for m in obj.metadata.items():
                if m.name in dict:
                    obj.metadata.remove(m)
                
            for key in dict:
                if ( key != 'path'):
                    if ( not key.endswith('-units')):
                        obj.metadata.add(key,dict[key], dict[key+'-units'])
    
    return data 


def put_object(irods_user, local_file, irods_file):

    with TuRODSSession(irods_user) as session:
        session.data_objects.put( local_file, irods_file)


def put_collection(irods_user, collection):

    with TuRODSSession(irods_user) as session:
        session.collections.create('/' + collection)
     


