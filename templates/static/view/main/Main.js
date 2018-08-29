

Ext.define('iRods.view.main.Main', {
    extend: 'Ext.panel.Panel',
    
    requires: [
        'iRods.view.main.tree',
        'iRods.view.main.metadata',
        'iRods.view.main.filter',
        'iRods.view.main.images',
        'iRods.view.main.MainController',
    ],
    autoScroll: true,
    xtype: 'app-main',
    controller: 'maincontroller',
    
    layout: 'border',
    
    items: [
    	{
            title: 'Metadata ...',
            region: 'east',     // position for region
            xtype: 'irods_metadata',
            id: 'irods_metadata',

            width: 720,
            split: true,         // enable resizing
            margin: '0 5 5 5',
        },
        {
            title: 'Filters',
            bodyPadding: 7,
            region: 'west',
            collapsible: true,
            width: 520,
            autoScroll: true,
            layout: 'column',
          	labelAlign: 'top',
          	split: true,
            xtype: 'irods_filter',
            id: 'irods_filter',
        },
        {
	        region:'south',
	        collapsible: true,   // make collapsible
            xtype: 'panel',
            layout: 'border',
            header: false,
            height: 475,
            split: true,
            bodyStyle: "background: lightblue",
            items: [ 
            	{xtype: 'panel', region: 'south', height: 20, bodyStyle: "background: lightgrey",}, 
            	{xtype: 'irods_images', region: 'center', title: 'Images'}]

        },
        {
        	title: 'Collections and Objects',
        	region: 'center',     // center region is required, no width/height specified
	        animate: false,
	        margin: '0 5 0 0 ',	 
            id: 'irods_tree',
	        xtype: 'irods_tree',         
	    },
	    {
		id: 'statusBar',
		 xtype: 'panel',
	    region: 'south',
	    height: 20,
	    bodyStyle: "background: lightgrey",
	    }
    
    ],
});


