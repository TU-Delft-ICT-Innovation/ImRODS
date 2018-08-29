# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import uuid
from irodsapp.irods_interface import get_metadata, put_object, get_collection_id
from irodsapp import irods_interface, irods_permissions
import irods.exception as ex
from django.core.exceptions import PermissionDenied
from .models import Thumbnail, UserIrodsMetaDataAttribute
from .gui_session import get_thumbs_ids, set_thumbs_ids, delete_thumbs_ids
from .gui_session import set_metadata_filters, get_metadata_filters, get_folder_metadata_filter
from .gui_session import get_allowed_ids, set_coll_ids_by_coll_filter, set_coll_ids_by_obj_filter
from anytree import Node
from anytree.exporter import DictExporter



def create_filter_dict_element(att_name, att_type, sessionFilters):
    
    att_dict = {}
    att_dict['key'] = att_name
    att_dict['type'] = att_type
 
    filter_starting_names = [
        {'name': 'obj-gt-', 'key': 'gt'},
        {'name': 'obj-lt-', 'key': 'lt'},
        {'name': 'obj-eq-', 'key': 'equals'},
        {'name': 'obj-lk-', 'key': 'lk'},
        {'name': 'obj-be-', 'key': 'be'},
        {'name': 'obj-af-', 'key': 'af'},
        {'name': 'obj-on-', 'key': 'on'},
        {'name': 'obj-tb-', 'key': 'tb'},
        {'name': 'obj-ta-', 'key': 'ta'},
        {'name': 'obj-to-', 'key': 'to'},

        {'name': 'col-gt-', 'key': 'gt'},
        {'name': 'col-lt-', 'key': 'lt'},
        {'name': 'col-eq-', 'key': 'equals'},
        {'name': 'col-lk-', 'key': 'lk'},
        {'name': 'col-be-', 'key': 'be'},
        {'name': 'col-af-', 'key': 'af'},
        {'name': 'col-on-', 'key': 'on'},
        {'name': 'col-tb-', 'key': 'tb'},
        {'name': 'col-ta-', 'key': 'ta'},
        {'name': 'col-to-', 'key': 'to'},  
        ]

    if sessionFilters is not None:
        for nm in filter_starting_names:
            name = nm['name'] + att_name
            if name in sessionFilters:
                att_dict[nm['key']] = sessionFilters[name]
   
    return att_dict                                         
        
def index_common(request, html_page):
    if not request.user.is_active:
        print ('raise PermissionDenied')
        raise PermissionDenied

    session = request.session
    filters = []
    collection_filters = []
    folder = get_folder_metadata_filter(session, '')

    sessionFilters = get_metadata_filters(session)
    
    for uima in UserIrodsMetaDataAttribute.objects.filter(user=request.user, object_or_collection=True, use_in_filters=True):
        filters.append( create_filter_dict_element(uima.name, uima.type, sessionFilters) )
            
    for uima in UserIrodsMetaDataAttribute.objects.filter(user=request.user, object_or_collection=False, use_in_filters=True):
        collection_filters.append( create_filter_dict_element(uima.name, uima.type, sessionFilters) )

    ctx = {
        'filters': filters, 
        'collection_filters': collection_filters, 
        'folder': folder,
        'image_columns' : request.user.profile.image_columns
        }

    return render(request, html_page, context=ctx)


@login_required(login_url="/admin/login/")
def index(request):

    return index_common(request, 'index.html')

def folder_detail(request, path):
    profile = request.user.profile
    return JsonResponse(get_metadata(profile.irods_user, path,True))
    
@login_required(login_url="/admin/login/")
def get_thumbnails_folder(request):
    
    data = {}
    data['pictures'] = [] 
    
    coll_id = request.POST.get('coll_id', None)
    thumb_id = request.POST.get('thumb_id', None)
         
    lst_thumbs_ids = []
    if coll_id is not None:
        all_ids = get_thumbs_ids(request.session)

        lst_thumbs_ids = all_ids[coll_id] if (coll_id in all_ids) else None 
    elif thumb_id is not None:
        lst_thumbs_ids.append(thumb_id)

    if lst_thumbs_ids is not None:
        thumbs = Thumbnail.objects.filter(id__in=lst_thumbs_ids)
        nn = 0
        for th in thumbs:
            data['pictures'].append( {'data' : th.image, 'name' : th.name})
            nn += 1
            if nn > 99:
                break

    return JsonResponse(data)
 

def humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.3f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.3f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.3f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.3f} TB'.format(B/TB)


def get_size(request):
    profile = request.user.profile
    size = irods_interface.get_size(profile.irods_user)
    return JsonResponse({ 'size':  humanbytes(size) + ' used'})  


def detail(request, path):

    profile =  request.user.profile    
    response = get_metadata(profile.irods_user,path, False)
    return JsonResponse(response)


def folders(request):
    profile = request.user.profile
    
    folders = irods_interface.folders(profile.irods_user, profile.root)
    
    return JsonResponse({ 'topics' : folders})

@login_required(login_url="/admin/login/")
def permissions(request):
    
    try:
        permissions = irods_permissions.permissions(True, request.POST['path'])
        return JsonResponse({ 'permissions' : permissions, 'error': None})
    except Exception as e:
        return JsonResponse({ 'error' : str(e)})


def set_metadata(request):
    
    profile = request.user.profile
    irods_interface.set_metadata(profile.irods_user, request.POST, False)
    data = {}
    return JsonResponse(data)


def set_metadata_folder(request):
      
    profile = request.user.profile    
    irods_interface.set_metadata(profile.irods_user, request.POST, True)
    data = {}
    return JsonResponse(data)


def upload(request):

    name = str(uuid.uuid4())
    filename = '/tmp/' + name
    print('upload to', filename)
    try:
        with open(filename, 'wb+') as destination:
         
            filep = request.FILES['file']
            for chunk in filep.chunks():
                destination.write(chunk)
    except Exception as e:
        print('EXCEPTION', str(e))

    dest = request.POST['path'] + '/' + request.FILES['file'].name
    profile =  request.user.profile

    try:
        put_object(profile.irods_user,filename, dest)
    except Exception as e:
        print(e)
        return JsonResponse({ 'error' : str(e)})

    return JsonResponse({})   



def put_collection(request, collection):
    
    profile =  request.user.profile
    try:
        irods_interface.put_collection(profile.irods_user, collection)
        return JsonResponse({})
    except ex.CAT_NO_ACCESS_PERMISSION:
        return JsonResponse({'error': 'No access permission'})
    except ex.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
        return JsonResponse({'error': 'Collection already exists'})


def get_tree(request):
        
    session = request.session
    filters = get_metadata_filters(session)
    thumbs_ids = get_thumbs_ids(session)
    allowed_collection_ids = get_allowed_ids(session)
    
    node = request.GET.get('node')
    profile = request.user.profile
    is_root = node == 'root'

    if is_root:
        node = get_folder_metadata_filter(session, profile.root)        
        root = Node('coll.name', id=1,path='coll.path')


        if False:
            for no in node.split(';'):
                thumbs_ids_collection, coll_id = irods_interface.get_tree_root(no, profile.irods_user, filters, allowed_collection_ids, root)

        else:
            thumbs_ids_collection = None            
            if allowed_collection_ids is None: 
                for no in node.split(';'):
                    coll_id = get_collection_id(no)
                    Node(no, root, id=coll_id, path=no, expanded=False)               
            else:
                for key in sorted(allowed_collection_ids.keys()):
                    Node(key, root, id=allowed_collection_ids[key], path=key, expanded=False)


    else:
        root, thumbs_ids_collection, coll_id = irods_interface.get_tree(node, profile.irods_user, filters, allowed_collection_ids)
        thumbs_ids[coll_id] = thumbs_ids_collection

    if root is not None:
        exporter = DictExporter()
        tree = exporter.export(root)
    else:
        tree = {}

    set_thumbs_ids(session,thumbs_ids)
    
    return JsonResponse(tree)


def set_filter(request):
    session = request.session
    
    filters = request.POST
    set_metadata_filters(session, filters)

    # new filter : clear the filtered thumbs id's
    delete_thumbs_ids(session)
    
    starting_folder = get_folder_metadata_filter(session, request.user.profile.root)

    coll_ids_by_coll_filter, coll_ids_by_obj_filter = irods_interface.set_filter(request.user, filters, starting_folder)
    
    set_coll_ids_by_coll_filter(session,coll_ids_by_coll_filter)
    set_coll_ids_by_obj_filter(session, coll_ids_by_obj_filter)

    return JsonResponse({})

def update_permissions(request):
    recursive = request.POST.get('recursive', False)
    user = request.POST.get('user', None)
    access = request.POST.get('access', None)
    name = request.POST.get('name', None)
    
    if access is None or user is None or name is None:
        return JsonResponse({'error': 'Missing required arguments'})

    try:
        irods_permissions.update_permissions( user, access, recursive, name);
        return JsonResponse({})
    except Exception as e:
        return JsonResponse({'error': str(e)})


