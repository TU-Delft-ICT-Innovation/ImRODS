

Ext.define('iRods.view.main.filter', {
    extend: 'Ext.Panel',

    /* Marks these are required classes to be to loaded before loading this view */
    requires: [
        'iRods.view.main.MainController',
    ],
       
    xtype: 'irods_filter',
    controller: 'maincontroller',
    
    
    initComponent: function () {
    	
    	this.callParent(); //added this to not break inheritance
    	
        var comboStore = Ext.create('Ext.data.Store', {
            fields: [{name: 'display'}, {name: 'value'}],
            autoLoad: true,
           
            proxy: {
            	type: 'ajax',
            	url: '/folders',
            	reader: {
            		type: 'json',
            		root: 'topics'
            	}
        	}, 	
    		});     
        

    	this.add({
    		topoffset: "10",
    		xtype: 'combobox',
    		typeAhead  : true,
    		//forceSelection: true,
    		editable: true,
    		queryMode: 'local',
    		fieldLabel: 'Folder',
    		store: comboStore,
    		displayField: 'display',
    		valueField: 'value',
    		name: 'Folder',
    		margin:'1 1 1 0',
    		value: folder,
    	});    
    	
        this.addFilters(filters, 'Object filters', 'obj');
        this.addFilters(collection_filters, 'Collection filters', 'col');  
    },
    
    
    get_post_data: function() {
    	
		var items = this.items.items;
		var postData = {};
		var item, str;
		// The first item is the folder, skip it
		for ( var x = 0; x < items.length; x++) {
			if (x == 0) {
				item = items[0];
				if (item.value != null ) {
        			str = String(item.value);
        			str = str.trim();
        			if (str.length > 0) {
    					postData[item.name] = str;   				
        			}     
				}
			} else {
				
    			var framedpanel = items[x];
    			if (framedpanel.id.lastIndexOf('label', 0) !== 0 ) {
        			var framedpanel_items = framedpanel.items.items;
        			
        			for ( var i = 0; i < framedpanel_items.length; i++) {
        				item = framedpanel_items[i];
        				if (item.value != null ) {

	            			// is it a datefield ?
	            			if (item.id.lastIndexOf('datefield', 0) === 0 ) {
	            				var dt = item.lastValue;
		            			if (dt.length > 0) {
		        					postData[item.name] = dt; 	
		            			}
	            			} else if (item.id.lastIndexOf('timefield', 0) === 0 ) {
		            				var dt = item.lastMutatedValue;
			            			if (dt.length > 0) {
			        					postData[item.name] = dt; 	
			            			}			            								            			
	            			} else {
	            				
		            			str = String(item.value);
		            			str = str.trim();			            				
		            			if (str.length > 0) {
		        					postData[item.name] = str;   				
		            			}			            				
	            			}
        				}
        			}
    			}
			}
		}  
		return postData;
    },
        
    addFilters: function(filters, heading, prefix) {
        if (filters.length > 0) {

        	this.add({
	    		xtype: 'label',
	        	html: "<br/>" + heading,
	        	style: 'font: normal 18px courier',
	     
	    	});	
        }
    	
        for (var n = 0; n < filters.length; n++) {
        	var f = filters[n];
        	
    		if (f.type == 'St')
    			this.addStringFilterEntry(f.key, prefix + '-lk-' + f.key, f.lk);
    		else if (f.type == 'De')
    			this.addDecimalFilterEntry(f.key,  prefix + '-gt-' + f.key, f.gt,  prefix + '-lt-'+f.key, f.lt,  prefix + '-eq-' + f.key, f.equals);	
    		else if ( f.type == 'Ti')
    			this.addTimeFilterEntry(f.key,  prefix + '-ta-' + f.key, f.ta,  prefix + '-tb-' + f.key,f.tb,  prefix + '-to-' + f.key, f.to);	
    		else if (f.type == 'Da')
    			this.addDateFilterEntry(f.key,  prefix + '-af-' + f.key, f.af,  prefix + '-be-' + f.key, f.be, prefix + '-on-'+ f.key, f.on);	
        }
    },
    

    addStringFilterEntry: function (title, name, value) {
    	this.add({
    		xtype: 'fieldset',
			collapsible: true,
        	title: title,
        	defaultType: 'textfield',
        	defaults: {
        		anchor: '100%',
            	labelSeparator : ''
         	},
        	items: [ { fieldLabel: 'like', name: name, value: value}]   
		});	
    },
    
    addDecimalFilterEntry: function (title, gt_name, gt_value, lt_name, lt_value, eq_name, eq_value) {
    	this.add({
    		xtype: 'fieldset',
			collapsible: true,
        	title: title,
        	defaultType: 'numberfield',
        	defaults: {
        		anchor: '100%',
            	labelSeparator : ''
         	},
        	items: [
            	{ fieldLabel: '>', name: gt_name, value: gt_value},
            	{ fieldLabel: '<', name: lt_name, value: lt_value},
            	{ fieldLabel: '=', name: eq_name, value: eq_value}
        	]   
		});		
	},
	
	
	addDateFilterEntry:  function (title, af_name, af_value, be_name, be_value, on_name, on_value) {
		this.add({
			xtype: 'fieldset',
			collapsible: true,
    		title: title,
    		defaultType: 'datefield',
    		defaults: {
    			anchor: '100%',
        		labelSeparator : ''
     		},
    		items: [
        		{ fieldLabel: '>', name: af_name, value: af_value},
        		{ fieldLabel: '<', name: be_name, value: be_value},
        		{ fieldLabel: '=', name: on_name, value: on_value}
    		]   
		});	    	
    },
    
    addTimeFilterEntry : function (title, af_name, af_value, be_name, be_value, on_name, on_value) {
    	this.add({
			xtype: 'fieldset',
			collapsible: true,
    		title: title,
    		defaultType: 'timefield',
    		defaults: {
    			anchor: '100%',
        		labelSeparator : '',
        		increment: 30,
        		format: 'H:i'
     		},
    		items: [
        		{ fieldLabel: '>', name: af_name, value: af_value},
        		{ fieldLabel: '<', name: be_name, value: be_value},
        		{ fieldLabel: '=', name: on_name, value: on_value}
    		]   
		});	    	
    },
	
	
    

    /* View model of the view */
    
	defaults: {
  		xtype: 'container',
		layout: 'form',
      	columnWidth: 1,
      	labelWidth: 150,
      	labelAlign: 'top',
  	},
		tbar: [
        {
            text: 'Apply',
            handler: 'onApplyFilter',
        }
    ],

    
});