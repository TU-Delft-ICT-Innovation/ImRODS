from irods.models import User as IrodsUser, CollectionAccess, Collection, UserGroup
from irods.query import SpecificQuery
from irods.exception import CAT_NO_ROWS_FOUND
from irodsapp.turodssession import TuRODSSession
from irodsapp.util import log_and_raise_exception


## global
def get_permissions_dict():
    permissions_dict = {}
    with TuRODSSession() as session:

        sql = "select token_id, token_name from R_TOKN_MAIN"
        columns = [CollectionAccess.user_id, CollectionAccess.name]
        alias = 'get_permissions_codes' 
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        exception = None
                
        try:
            for result in query.get_results():
                token_id = result[CollectionAccess.user_id]
                name = result[CollectionAccess.name]
                permissions_dict[token_id] = name
 
        except Exception as e:
            exception = e
        
        _ = query.remove()  
        
        if exception is not None:
            log_and_raise_exception('Error in get_permissions_dict', exception)
    
    return permissions_dict

permissions_dict = get_permissions_dict()

def get_access_type_id(access):
    return list(permissions_dict.keys())[list(permissions_dict.values()).index(access)]


def get_collection_name(coll_id):
    with TuRODSSession() as session:
        query = session.query(Collection.name).filter(Collection.id == coll_id)
        result = query.execute()
        return result[0][Collection.name]
    return None


def get_collection_id(name):
    with TuRODSSession() as session:
        query = session.query(Collection.id).filter(Collection.name == name)
        result = query.execute()
        if len(result) > 0:
            return result[0][Collection.id]
    return None

def delete_permission(user_id, object_id):
    
 
    with TuRODSSession() as session:

        sql = "delete from R_OBJT_ACCESS WHERE object_id = {} and user_id = {}".format(object_id, 24746)
        alias = 'del_permissions' 

        query = SpecificQuery(session, sql, alias)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None

        try:
            query.execute()
            query.get_results()
        except Exception as e:
            exception = e

        # delete specific query
        _ = query.remove()
        
        if exception is not None:
            log_and_raise_exception('Error in delete_permission', exception)


def testje(path, user_id):
    with TuRODSSession() as session:
        sql = "select object_id from R_OBJT_ACCESS where user_id = {} and object_id in" \
        "(select R_COLL_MAIN.coll_id from R_COLL_MAIN WHERE R_COLL_MAIN.coll_name like '{}%' )". \
        format(user_id, path)
        
        
        
        sql = "select R_COLL_MAIN.coll_id from R_COLL_MAIN JOIN R_OBJT_ACCESS ON R_COLL_MAIN.coll_id = R_OBJT_ACCESS.object_id " \
        "WHERE R_COLL_MAIN.coll_name like '{}% and R_OBJT_ACCESS.user_id = {}".format(path, user_id)
        
        
        sql = "select R_COLL_MAIN.coll_id from R_COLL_MAIN " \
                "JOIN R_OBJT_ACCESS OA ON OA.object_id = R_COLL_MAIN.coll_id " \
                "WHERE user_id = " + str(user_id)
        
        
        
        #sql = "select R_COLL_MAIN.coll_id from R_COLL_MAIN WHERE R_COLL_MAIN.coll_name like '{}%' ".format(path)        
        print(sql)
        
        alias = 'blepper14'
        columns = [Collection.id]
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None
        n = 0
        try:
            query.execute()
            for result in query.get_results():
                n=n+1
                print(n,result[Collection.id])
                
                print(get_collection_name(result[Collection.id]))
                
                
        except CAT_NO_ROWS_FOUND:
            print('no exception')
        except Exception as e:
            exception = e

        _ = query.remove()   
                
        if exception is not None:
            log_and_raise_exception('Error', exception)   


def show_groups(users_dict):
    with TuRODSSession() as session:
        
        
        query = session.query(UserGroup.id, UserGroup.name)
        for result in query.get_results():
            print(result[UserGroup.id], result[UserGroup.name])
        
        
        sql = "select group_user_id, user_id from R_user_group"
        
        alias = 'blepper15'
        columns = [CollectionAccess.user_id, CollectionAccess.access_id]
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None
        n = 0
        try:
            query.execute()
            for result in query.get_results():
                n=n+1
                user = users_dict[result[CollectionAccess.access_id]]
                #print(n,result[CollectionAccess.user_id], user)
                print(result[CollectionAccess.user_id], result[CollectionAccess.access_id])
                
                
        except CAT_NO_ROWS_FOUND:
            print('no exception')
        except Exception as e:
            exception = e

        _ = query.remove()   
                
        if exception is not None:
            log_and_raise_exception('Error', exception)    
        
def update_permissions( user, access, recursive, name):
    
    access_type_id = get_access_type_id(access)
    object_id = get_collection_id(name)    
    users_dict = get_user_dict()    
    user_id = list(users_dict.keys())[list(users_dict.values()).index(user)]    
    
    with TuRODSSession() as session:
        sql = "update R_OBJT_ACCESS set access_type_id = {} where object_id = {} and user_id = {}" \
            .format(access_type_id, object_id, user_id)
        
        alias = 'update_permissions2'
        query = SpecificQuery(session, sql, alias)
        
        # register specific query in iCAT
        _ = query.register()
        
        exception = None
        try:
            query.execute()
        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e

        _ = query.remove()   
                
        if exception is not None:
            log_and_raise_exception('Error in changing the permissions access_type_id = {} object_id = {} and user_id = {}' \
                        .format(access_type_id, object_id, user_id), exception)


def get_user_dict():
    users_dict = {}
    
    with TuRODSSession() as session:
        query = session.query(IrodsUser)
        for result in query.get_results():
            users_dict[result[IrodsUser.id]] = result[IrodsUser.name]
    return users_dict
            

def permissions(folder, name):

    users_dict = get_user_dict()
    show_groups(users_dict)
    
    with TuRODSSession() as session:
        coll = session.collections.get(name)
        
    permission = []
    user_with_permissions = {}
    
    with TuRODSSession() as session:

        sql = "select user_id, access_type_id from R_OBJT_ACCESS WHERE object_id = {}".format(coll.id)
        columns = [CollectionAccess.user_id, CollectionAccess.access_id]
        alias = 'get_permissions' 
        query = SpecificQuery(session, sql, alias, columns)
        
        # register specific query in iCAT
        _ = query.register()
        exception = None
        
        try:
            for result in query.get_results():
                usr_id = result[CollectionAccess.user_id]
                access_id = result[CollectionAccess.access_id]
                permission.append({
                    'user': users_dict[usr_id],
                    'access': permissions_dict[access_id],
                    'hasRights': True
                    })
                user_with_permissions[usr_id] = usr_id
                print(usr_id, users_dict[usr_id])

        except CAT_NO_ROWS_FOUND:
            pass
        except Exception as e:
            exception = e
        
        _ = query.remove()

        if exception is not None:
            log_and_raise_exception('Error fetching permissions', exception)
        
        for usr_id in users_dict:
            if usr_id not in user_with_permissions:
                permission.append({
                    'user': users_dict[usr_id],
                    'access': '',
                    'hasRights': False
                    })                
                 
    return permission

