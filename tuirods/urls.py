"""irods URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin


from .adminsitewithexternalauth import AdminSiteWithExternalAuth
admin.site = AdminSiteWithExternalAuth()
admin.autodiscover()

from irodsapp.views import index, get_tree, detail,  upload, set_metadata, set_metadata_folder, update_permissions
from irodsapp.views import folders, put_collection, get_size, set_filter, folder_detail, get_thumbnails_folder, permissions
from irodsapp.report import create_report


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^saml2/', include('djangosaml2.urls')),

    url(r'^$', index, name='index'),
    
    url(r'^forum-data.json$', get_tree, name='get_tree'),

   # url(r'^get_sub_tree/(?P<path>.+?)/$', get_sub_tree, name='get_sub_tree'),
    
    url(r'^detail/(?P<path>.+?)/$', detail),
    url(r'^folderdetail/(?P<path>.+?)/$', folder_detail),
    
    url(r'^get_thumbnails_folder/$', get_thumbnails_folder),
        
    url(r'^set_metadata/$', set_metadata),
    url(r'^set_metadata_folder/$', set_metadata_folder),
    
    url(r'^upload$', upload, name='upload'),
        
    url(r'^folders$', folders, name='folders'),
    url(r'^permissions$', permissions, name='permissions'),
    
    url(r'^put_collection/(?P<collection>.+?)/$', put_collection),
    url(r'^get_size$', get_size, name='get_size'),
    url(r'^filter$', set_filter, name='set_filter'),
    
    #url(r'^create_report/(?P<coll_id>.+?)/$', create_report),
    url(r'^create_report/$', create_report),
    url(r'^update_permissions/$', update_permissions),
    
    
]
