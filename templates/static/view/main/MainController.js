Ext.define('iRods.view.main.MainController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.maincontroller',
    views: ['iRods.view.main.Main'],

    
    init: function () {
    
    },
    
    getMetadataForm: function() {
    	return Ext.getCmp('irods_metadata');
    },
    
    getTree: function() {
    	return Ext.getCmp('irods_tree');
    },
    
    getFilterPanel: function() {
    	return Ext.getCmp('irods_filter');
    },
    

    onCreateReport: function() {
    	var tree = this.getTree();
    	var node = tree.getSelectionModel().getSelection()[0];
    	var coll_id = ''
    	if (node !== undefined)
    		coll_id = node.data['id'] ;
    	
    	document.getElementById('nb_of_columns').value = Ext.getCmp('columns').getValue();
    	//document.getElementById('sub_collections').value = Ext.getCmp('add_images').getValue();
    	document.getElementById('sub_collections').value = true;
    	document.getElementById('coll_id').value = coll_id ;  	
    	document.getElementById('TheForm').submit();
    },    
    
    
    onApplyFilter: function() {
    	console.log('mainController onApplyFilter');
    	var form = this.getMetadataForm()
    	var filterPanel = this.getFilterPanel();
    	var tree = this.getTree();
    	
    	form.removeAll();
    	form.setTitle('MetaData');
	
    	var postData = filterPanel.get_post_data();
    	console.log(postData);
    	
		console.log('POSTDATA', postData);
        Ext.Ajax.request({
            url:  '/filter',
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', "X-CSRFToken":  csrf_token },
			params: postData,                    
            success: function (response) {
            	tree.store.load();
            },
            failure: function (response) {
                Ext.Msg.alert('Status', 'Request Failed.');
            }
        }); 
    },
    
    
    onAddMetaDataAttribute: function() {
    	this.getMetadataForm().addMetaDataAttribute();
    },
    
    onSaveMetaData: function() {
    	var tree = this.getTree();
    	var form = this.getMetadataForm();

		var parent = tree.getSelectionModel().getSelection()[0];
		var record = parent.data;
		var postData = form.get_post_data(parent.data['path']);

		
     	var path = '';
     	console.log(record);
     	if (record['leaf']) {
             path = '/set_metadata/';
     	} else {
             path = '/set_metadata_folder/';
     	}
     	
         Ext.Ajax.request({
         	
             url:  path,
             method: 'POST',
             headers: { 
            	 'Content-Type': 'application/x-www-form-urlencoded', 
            	 "X-CSRFToken":  csrf_token 
             },
             params: postData,              
             success: function (response) {
             	
            	 for ( var i = 0; i < form.items.items.length; i++) {
            		 var item = form.items.items[i];
         				if ( item.isDirty() ) {
         					item.originalValue = item.value;                				
         				}
         			}
             	var SaveBtn = Ext.getCmp('Save_Btn');
             	SaveBtn.disable();
             },
             failure: function (response) {
                 Ext.Msg.alert('Status', 'Request Failed.');
             }
         }); 
    	
    },
    
    onRowEditorEdit: function(editor, ctx, eOpts) {
    	
    	var tree = this.getTree();
		var parent = tree.getSelectionModel().getSelection()[0];
		var path = parent.data['path'];
    	
    	
        ctx.grid.getStore().sync();  // Force a post with the updated data.
                
        var recursive = Ext.getCmp('id_on_sub_folders').getValue();
		var postData = {};
		postData['recursive'] = recursive;
		postData['user'] =  ctx.record.data.user;
		postData['access'] =  ctx.record.data.access;
		postData['name'] =  path;
		
        
        Ext.Ajax.request({
            url: '/update_permissions/',    // where you wanna post
            success: function(response){
				var json = Ext.decode(response.responseText);
				if (json.error !== undefined) {
					Ext.Msg.alert('Error', json.error);
				} else {
 	               //permStore.loadData(json.permissions);
				}
            },
            
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', "X-CSRFToken":  csrf_token},
			params: postData,               
        });
        
    }, 
    
    
    createPermissionsGrid: function(node, path) {
    	
        var permStore = Ext.create('Ext.data.Store', {
            fields: [{name: 'user'}, {name: 'access'}],	
    		});   

		var postData = {};
		postData['path'] = path;
    	
        Ext.Ajax.request({
            url: '/permissions',    // where you wanna post
            success: function(response){
               	var json = Ext.decode(response.responseText);
				if (json.error !== null) {
					Ext.Msg.alert('Status', json.error);
				} else {
 	               permStore.loadData(json.permissions);
				}
            },
            
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', "X-CSRFToken":  csrf_token },
			params: postData,               
        });

        var grid = Ext.create('Ext.grid.Panel', {
            height: 800,
            store: permStore,
            columns: [
                { header: 'Has rights?', dataIndex: 'hasRights', xtype: 'checkcolumn', processEvent: function () { return false; } },

// 				{
//                 xtype:'checkcolumn',
//                 fieldLabel: 'checkbox_label',
//                 name: 'checkbox_name',
//                 text: 'Has rights?',
//                 dataIndex: 'hasRights',
//                 },
                { header: "<b>User</b>", dataIndex: 'user', flex: 1 },
                {
                    header: "<b>Access</b>",
                    sortable: false,
                    width: 150,
                    dataIndex: 'access',
	                editor: new Ext.form.ComboBox({
	                    triggerAction: 'all',
	                    emptyText: 'Select Field...',
	                    editable: false,
	                    forceSelection: false,
	                    valueField: 'access',
	                    displayField: 'name',                   
	                    store: new Ext.data.SimpleStore({
 	                        fields: ['name', 'access'],
 	                        data: [["own", "own"], ["read object", "read object"], ["modify object", "modify object"], ["None", "None"]]                    
 	                    }),
	                    mode: 'local',
	                }),

                }                
            ],
			selType: 'rowmodel',
            plugins: {
            	ptype: 'rowediting',
				clicksToEdit: 1,
				pluginId: 'roweditingId',
				listeners: {
					edit: this.onRowEditorEdit
				}
			},			
	        tbar: [
	        	{
	        		xtype: 'checkbox',
        	       	boxLabel: 'Apply to all subcollections and files?',
        	       	id : 'id_on_sub_folders'
        	    },        	    
//         	    {
// 	            	text: 'Add User',
// 	            	iconCls: 'employee-add',
// 		            handler : function() {
// 		            	var rowediting = grid.getPlugin('roweditingId');
// 		            	rowediting.cancelEdit();
// 		            	permStore.insert(0,  {user: 'NewGuy', access: 'modify object',});
// 		            	rowediting.startEdit(0, 0);  
// 	            }
//	        }, 
/* 	        {
	            itemId: 'removeUser',
	            text: 'Remove user',
	            iconCls: 'employee-remove',
	            handler: function() {
// 	                var sm = grid.getSelectionModel();
// 	                rowEditing.cancelEdit();
// 	                store.remove(sm.getSelection());
// 	                if (store.getCount() > 0) {
// 	                    sm.select(0);
// 	                }
	            },
	            disabled: true
	        } */
	        ],			


        });        
        return grid;
    	
    },    
    
    
    
    createUploadGrid: function (node, path) {
    	var store = this.getTree().getStore();
    	console.log(node);
    	console.log(path);
    	
        var grid = Ext.widget({
            xtype: 'grid',
            height: 400,
            store: {
                fields: ['name', 'size', 'progress', 'status']
            },
            tbar: [{
                xtype: 'filefield',
                buttonOnly: true,
                width: 10,
                listeners: {
                    render: function (s) {
                        s.fileInputEl.set({ multiple: 'multiple' });
                    },
                    change: function (s) {
                        Ext.each(s.fileInputEl.dom.files, function (f) {
                            var data = new FormData(),
                                rec = grid.store.add({ name: f.name, size: f.size, status: 'queued' })[0];
                            console.log(f);
                            data.append('file', f);
                            data.append('path', path);
                            Ext.Ajax.request({
                                url: '/upload',
                                timeout: 160000,
                                rawData: data,
                                
                                headers: {'Content-Type': null, "X-CSRFToken": csrf_token}, //to use content type of FormData

                                progress: function (e) {
                                    rec.set('progress', e.loaded / e.total);
                                    rec.set('status', 'uploading...');
                                    rec.commit();
                                },
                                success: function (response) {
                                	var json = Ext.decode(response.responseText);
                                	console.log(json);
        							if (json.error !== undefined) {
                                        rec.set('progress', 0);
                                        rec.set('status', 'failed');
                                        rec.commit();
        								Ext.Msg.alert('Error', json.error);
        							} else {
        								                                	
	                                    rec.set('status', 'done');
	                                    rec.commit();
	                                    
	                                    node.removeAll();
	                                    store.load({ 
	                                        node: node, 
	                                    });
        							}   
                                },
                                failure: function () {
                                    rec.set('progress', 0);
                                    rec.set('status', 'failed');
                                    rec.commit();
                                }
                            });
                        });
                    }
                }
            }],
            columns: [
                { text: 'Name', dataIndex: 'name', flex: 1 },
                { text: 'Status', dataIndex: 'status', width: 100 },
                {
                    text: 'Progress', xtype: 'widgetcolumn', widget: {
                        xtype: 'progressbarwidget',
                        textTpl: [
                            '{percent:number("0")}%'
                        ]
                    }, dataIndex: 'progress', width: 100
                },
                { text: 'Size', dataIndex: 'size', width: 100, renderer: Ext.util.Format.fileSize }
            ],
            //renderTo: Ext.getBody()
        });    	
        
        return grid;
    	
    },
    
    itemcontextmenu: function(view, r, node, index, e) {
        e.stopEvent();
    	var tree = this.getTree();
    	var me = this;
		var parent = tree.getSelectionModel().getSelection()[0];
		var path = parent.data['path']

        var menu_grid;
        if ( r.data.leaf ) {
        	menu_grid = new Ext.menu.Menu({ 
        		items:[]
        	});                	
        } else {
        	menu_grid = new Ext.menu.Menu({ 
	      		items:[
	                { text: 'Show permissions', handler: function() {			                	
	                	var grid = me.createPermissionsGrid(r, path);

	                    var permWin = new Ext.Window({
	                        title: "Permissions for " + path,
	                        width: 640,
	                        modal:true,
	                        height: 600,
	                        layout: 'fit',
	                        items: [ grid,],
	                        resizable: false,
	                    });    			                	
	                    permWin.show();
	                	} 
	                },		      			
	                { text: 'Upload file here', handler: function() {			                	
	                	var grid = me.createUploadGrid(r, parent.data['path']);

	                    var uploadWin = new Ext.Window({
	                        title: "Upload window",
	                        width: 680,
	                        height: 300,
	                        items: [ grid,]
	                    });    			                	
	                	uploadWin.show();
	                	} 
	                },
	                { text: 'Create Collection', handler: function() {
	                	
	                	Ext.Msg.prompt("tudRods", "Enter the name of the collection", 
	                			function(btnText, sInput) {
	                				if(btnText === 'ok') {
	                					var uri = encodeURI('/put_collection/' + parent.data['path'] + '/' + sInput + '/');
												
	                					Ext.Ajax.request({
	                						url:  uri,
	                						method: 'GET',
	                						timeout: 60000,
	                						dataType: 'json',
	                						headers: { 'Content-Type': 'application/json' },
	                						success: function (response) {
	                							var json = Ext.decode(response.responseText);
	                							console.log(json.error);
	                							if (json.error !== undefined) {
	                								Ext.Msg.alert('Status', json.error);
	                							}
	                							else {
	                								r.appendChild({
	                									name : sInput,
	                									leaf : true,
	                								});
	                							}
	                						},
	                						failure: function (response) {
	                							Ext.Msg.alert('Status', 'Request Failed.');
	                						}
	                					});  													
	                				}
	                	}, this);
	                } 
	                },
	                ]
        	});
        }
        // HERE IS THE MAIN CHANGE
        var position = [e.getX()-10, e.getY()-10];
        e.stopEvent();
        menu_grid.showAt(position);
        return false;
    },
    
    select_changed: function(sm, selectedRecord) {
    	var me = this;
    	
        if (selectedRecord.length) {
        	var record = selectedRecord[0].data;
            var path = record['path'];
                        
            var parts = record['name'].split('/');
			var lastSegment = parts.pop();  // handle potential trailing slash
            
			var form = this.getMetadataForm();
			form.setTitle("MetaData '" + lastSegment + "'");
			
			Ext.getCmp('Save_Btn').disable();
			        	
        	Ext.suspendLayouts();
            selectedRecord[0].expand();
        	selectedRecord[0].expand(false, function(oChildren) {
				var postData = {};
        		if (oChildren === undefined ) {
        			var thumb_id = record['id'];
        			if (thumb_id !== null) {
            			postData['thumb_id'] = thumb_id; 
            			me.get_thumbnails(record, path, postData);
        			} else {
        		        me.imagepanel.removeAll();
        				Ext.resumeLayouts(true);
        			}
        			
        		} else {
        			
					postData['coll_id'] = record['id'];
					me.get_thumbnails(record, path, postData);
        		}
        	    
        	});
                        
        	/////////////////////////////
            // get detail info
            ///////////////////////
        	form.removeAll();
        	form.getEl().mask('Loading');
            
        	var uri = '';
            if (record['leaf'] == false) {
                uri = encodeURI('/folderdetail' + path);
        	} else {
                uri = encodeURI('/detail/' + path);
        	}
            form.get_metadata(uri);
        }
    },


	
    
    get_thumbnails: function (record, path, postData) {
    	
    	this.imagepanel = Ext.ComponentQuery.query("irods_images")[0];
        this.imagepanel.removeAll();
        this.imagepanel.getEl().mask('Loading');
        var uri = encodeURI('/get_thumbnails_folder/');
        var me = this;
    	        
        Ext.Ajax.request({
            url:  uri,
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded', "X-CSRFToken":  csrf_token },
            timeout: 60000,
            params: postData,
            dataType: 'json',
            //headers: { 'Content-Type': 'application/json' },
            success: function (response) {
            	var data = Ext.decode(response.responseText);
            	
            	var pictures = data.pictures;
            	console.log('pictures', pictures);
            	if ( pictures !== null) {
					var width = 1.0 / image_columns;
					if (pictures.length === 1) {
						width = 0.66;
					}
					
					for ( var xx in pictures ) {
						console.log('Doing picture', pictures[xx]['name']);
						var ii = Ext.create('Ext.Img', {
							src:  pictures[xx]['data'],
						    width: '100%',
						    //height: '100%',
							border:false,
							id: pictures[xx]['name'],
							listeners: {
						        el: {
						            dblclick: function() {
						            	var idd = this.id;
						            	console.log(idd);
						                var rec = store.findRecord('name', idd);
						                if ( rec !== undefined) {
							                tree.getSelectionModel().select(rec);						                	
						                }
						            }
						        }
						    },
						});
					    	
						var imagepanel1 = Ext.create('Ext.Panel', {
							bodyPadding: 7,
							columnWidth: width,
						  	border: false,
						   	bodyStyle: "background: #ffffff;",
							items: [
									ii,
						        	{ html: pictures[xx]['name'],	border: false}
						        	],
						    });
						console.log('me.imagepanel', me.imagepanel);
						console.log('me.imagepanel.items.length', me.imagepanel.items.length);
						me.imagepanel.insert(me.imagepanel.items.length, imagepanel1);	
					}            		
            	}
   	            me.imagepanel.getEl().unmask();
				Ext.resumeLayouts(true);
				
				me.imagepanel.scrollBy(0, 400, true);
				
			    task.delay(100);
            },
            failure: function (response) {
   	            me.imagepanel.getEl().unmask();
                Ext.Msg.alert('Status', 'Request Failed.');
                Ext.resumeLayouts(true);
    		    task.delay(100);
            }
        });      	
    }  
  

});


