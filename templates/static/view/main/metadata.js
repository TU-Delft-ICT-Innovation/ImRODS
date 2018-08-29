

Ext.define('iRods.view.main.metadata', {
    extend: 'Ext.form.Panel',

    /* Marks these are required classes to be to loaded before loading this view */
    requires: [
        'iRods.view.main.MainController',
    ],
       
    xtype: 'irods_metadata',
    controller: 'maincontroller',
    
    
    initComponent: function () {
    	
    	this.callParent(); //added this to not break inheritance        
    },
    
    setDirty: function () {
       	
        var SaveBtn = Ext.getCmp('Save_Btn');
       	if (this.isDirty())
           	SaveBtn.enable();
       	else {
           	SaveBtn.disable();       		
       	}
    },
    
    getvalue: function (items, key) {
   	 
    	for ( var i = 0; i < items.length; i++) {
    		var item = items[i];
    		
    		if (item.name === key) {
    			return item.value;
    		}
    	}
		return '';    	
    },    
    
    get_post_data: function(path) {
    	var postData = {};
		var units = '-units';
		postData['path'] = path
    	
		for ( var i = 0; i < this.items.items.length; i++) {
			var item = this.items.items[i];
				
			if ( item.isDirty() ) {
				var key = item.name;
				postData[key] = item.value;
				if (key.endsWith(units)) {
					key = key.substr(0, key.lastIndexOf(units));
				} 
				else {
					key = key+ units;
				}
				postData[key] = this.getvalue(this.items.items, key);
			}
		}
		return postData
    },
    
    
    addMetaDataAttribute: function() {
    	console.log('Add meta data attribute');
    	var me = this;
    	Ext.Msg.prompt("tudRods", "Enter the name of the attribute", function(btnText, sInput) {
    		if(btnText === 'ok'){
    			this.add({
    				topoffset: "10",
    				labelAlign : 'right',
    				xtype : 'textfield',
    				fieldLabel : sInput,
    				name : sInput,
    				value: "",
    				margin:'5 5 5 0',    	
    				listeners: {
    					render: function( component ) {
    						component.getEl().on('keyup', function( event, el ) {
    							me.setDirty();
    						});
    					}
    				}    			   		    			
    			});
    	
    			this.add({
    				labelAlign : 'right',
    				xtype : 'textfield',
    				fieldLabel : "Unit",
    				name : sInput + '-units',
    				value: "",
    				margin:'5 5 5 0',
    				listeners: {
    					render: function( component ) {
    						component.getEl().on('keyup', function( event, el ) {
    							me.setDirty();
    						});
    					}
    				}    			   		    			
    			});    
    		}
    	}, this);    	
    },    
    
    
    
    
    get_metadata: function (uri) {
    	console.log(uri);
        this.removeAll();
        this.getEl().mask('Loading');
        
        var me = this;
        console.log(this);
                
        Ext.Ajax.request({
            url:  uri,
            method: 'GET',
            timeout: 60000,
            dataType: 'json',
            headers: { 'Content-Type': 'application/json' },
            success: function (response) {
            	var json = Ext.decode(response.responseText);
		
				for (var i in json.metadata) {
					var entry = json.metadata[i];
					me.add({
				        labelAlign : 'right',
						xtype : 'textfield',
		    				fieldLabel : entry['key'],
		    				name : entry['key'],
		    				value: entry['val'],
							margin:'5 5 5 0',
			                labelWidth: 150,
			             	columnWidth: .7,
		    			listeners: {
   		    	            render: function( component ) {
   		    	                component.getEl().on('keyup', function( event, el ) {
									me.setDirty();
   		    	                });
   		    	            }
   		    	        }   							
		    				});
					me.add({
				        labelAlign : 'right',
						xtype : 'textfield',
		    				fieldLabel : 'Unit',
		    				name : entry['key'] + '-units',
		    				value: entry['units'],
   		    			margin:'5 5 5 0',
			             	columnWidth:.3,
   		                labelWidth: 50,
		    			listeners: {
   		    	            render: function( component ) {
   		    	                component.getEl().on('keyup', function( event, el ) {
									me.setDirty();
   		    	                });
   		    	            }
   		    	        }	   		    			
		    				});   						
				}
   	            me.getEl().unmask();
            },
            failure: function (response) {
   	            me.getEl().unmask();
                Ext.Msg.alert('Status', 'Request Failed.');
            }
        });    
    },
    
    
    bodyPadding: 7,
    collapsible: true,
    width: 720,
    autoScroll: true,
  	labelAlign: 'top',
  	trackResetOnLoad: true,
    labelWidth: 150,
       
    layout: 'column',
    defaults: {
    	xtype: 'container',
    	layout: 'form',
    	columnWidth: 0.5,
    	labelWidth: 150,
    	},

    buttons: [{
    	text: 'Save',
     	id: 'Save_Btn',
     	disabled: true,
     	handler: 'onSaveMetaData',
    },		
    ],
     
    tbar: [ {
    	text: 'Add Metadata attribute',
    	handler: 'onAddMetaDataAttribute',
    }
    ]     
     
    
});