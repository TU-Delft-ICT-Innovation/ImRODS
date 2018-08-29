

Ext.define('iRods.view.main.images', {
    extend: 'Ext.Panel',

    /* Marks these are required classes to be to loaded before loading this view */
    requires: [
        'iRods.view.main.MainController',
    ],
       
    xtype: 'irods_images',
    controller: 'maincontroller',
    
    
    initComponent: function () {
    	this.callParent(); //added this to not break inheritance
    },

    
    /* View model of the view */

    
	id: 'detailPanely',
    bodyPadding: 7,
    
    bodyStyle: "background: #ffffff;",
    items: [],
	layout:'column',
	autoScroll:true,
	title: 'Imagepanel',
	tbar: [
		{
        xtype: 'combobox',
        name: 'columns',
        fieldLabel: 'No of columns',
        id : 'columns',
        store: Ext.create('Ext.data.Store', {
            fields: ['abbr', 'name'],
            data : [
                {"abbr":"1", "name":"1"},
                {"abbr":"2", "name":"2"},
                {"abbr":"3", "name":"3"},
                {"abbr":"4", "name":"4"},
                {"abbr":"5", "name":"5"},
                {"abbr":"6", "name":"6"},
                {"abbr":"7", "name":"7"},
                {"abbr":"8", "name":"8"}
            ]
        }),
        queryMode: 'local',
        displayField: 'name',
        valueField: 'abbr',
        width: 180,
        listeners:{
        	afterrender:function(rec){
            	//Ext.getCmp('nb_of_columns').setValue('4');
            	rec.setValue('3');
        	}
        }
    },     
    { xtype: 'tbseparator' },
    {
        text: 'Report',
        handler: 'onCreateReport'        
    }
],
    
});



