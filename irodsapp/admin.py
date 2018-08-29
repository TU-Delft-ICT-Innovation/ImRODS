# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from .models import Profile, Thumbnail, Folder, Error, UserIrodsMetaDataAttribute



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Irods Settings'
    fk_name = 'user'
    
    #filter_horizontal = ('filters',)

    
    fields = (
        'irods_user', 'root', 'create_thumbs', 'image_columns'
        )

class CustomUserAdmin(UserAdmin):
    def root(self):
        return self.profile.root
    root.admin_order_field = 'profile__root'

    def create_thumbs(self):
        return self.profile.create_thumbs
    create_thumbs.admin_order_field = 'profile__create_thumbs'
    
    def irods_user(self):
        return self.profile.irods_user
    irods_user.admin_order_field = 'profile__irods_user'
        

    list_display = ('username', 'email', 'is_staff', 'last_login', root, irods_user, create_thumbs)
    
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# class FoldernameFilter(admin.SimpleListFilter):
#     title = _('Foldername')
#     parameter_name = 'action_flag'
# 
#     def lookups(self, request, model_admin):
#             
#         folders = Folder.objects.all()
# 
#         leafs = []
#         for c in folders:
#             leafs.append((c.id, (c.name)))
# 
#         return leafs
# 
#     def queryset(self, request, queryset):
#         if self.value() is not None:
#             return queryset.filter(foldername=self.value())
#         return queryset

class ThumbnailAdmin(admin.ModelAdmin):
    
    def folder_id_display(self, obj):
        return obj.folder_id
    folder_id_display.short_description = 'coll id'    
    

    search_fields = ('id', 'name',)
    #list_filter = ('folder',)
    list_display = ('id', 'name', 'folder_id_display')

#     list_select_related = (
#         'folder',
#     )
    
    
class FolderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)    
    search_fields = ('id', 'name',)
    

class UserIrodsMetaDataAttributeAdmin(admin.ModelAdmin): 
    
    change_list_template = 'irodsapp/change_list.html'


    def __init__(self, *args, **kwargs):
        super(UserIrodsMetaDataAttributeAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None
         
    def has_add_permission(self, request):
        return False    
 
    def get_actions(self, request):
        actions = super(UserIrodsMetaDataAttributeAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['delete_selected']
        return actions
    
    def get_queryset(self, request):
        if request.user.is_superuser:
            return UserIrodsMetaDataAttribute.objects.all()
        return UserIrodsMetaDataAttribute.objects.filter(user=request.user)    
    
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ('use_in_filters', 'object_or_collection', 'user')
        else:
            return ('use_in_filters', 'object_or_collection')
        
#     def get_list_display(self, request):
#         if request.user.is_superuser:
#             return super(UserIrodsMetaDataAttributeAdmin, self).get_list_display(request)
#         else:
#             return ('name', 'name_unique', 'type', 'use_in_filters', 'object_or_collection')   
    
    def type(self,obj):
        if 'St' == obj.att.type:
            return 'String'
        if 'De' == obj.att.type:
            return 'Decimal'        
        if 'Da' == obj.att.type:
            return 'Date'        
        return obj.att.type
    type.admin_order_field = 'att__type'


    search_fields = ('name',)
    
    list_editable = ('use_in_filters', 'type')
    list_display = ('name', 'name_unique', 'type', 'use_in_filters', 'object_or_collection', 'user')  
    
    list_per_page = 25
    

class ErrorAdmin(admin.ModelAdmin):   
    list_display = ('error', 'date')      
    


admin.site.register(Error, ErrorAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(UserIrodsMetaDataAttribute, UserIrodsMetaDataAttributeAdmin)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, GroupAdmin)