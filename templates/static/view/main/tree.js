Ext.define('IrodsModel', {
    extend: 'Ext.data.TreeModel',
    idProperty: 'path',
    fields: [{
        name: "name",
        convert: undefined
    },{
        name: "id",
        convert: undefined
    },{
        name: "path",
        convert: undefined
    }
    ]
});

Ext.define('iRods.view.main.tree', {
    extend: 'Ext.tree.Panel',

    /* Marks these are required classes to be to loaded before loading this view */
    requires: [
        'iRods.view.main.MainController',

    ],
       
    xtype: 'irods_tree',
    controller: 'maincontroller',
    
    listeners:{
        selectionchange: 'select_changed',
        itemcontextmenu : 'itemcontextmenu',
        
    },

    title: 'Collections and Objects',
    reserveScrollbar: true,
    loadMask: true,
    rootVisible: false,

    animate: false,
    //margin: '0 5 0 0 ',
    columns: [{
        xtype: 'treecolumn', //this is so we know which column will show the tree
        text: 'Name',
        width: 540,
        sortable: true,
        locked: true,
        dataIndex: 'name'
    },
     {
         text: 'id',
         width: 120,
         dataIndex: 'id',
         sortable: true
      },
     {        	
		text: 'size',
		dataIndex: 'size',
		 width: 150,
    },
    ],
    
    
    store: Ext.create('Ext.data.TreeStore', {
        model: 'IrodsModel',
        proxy: {
            type: 'ajax',
            api: {
                create: 'createPersons',
                read: 'forum-data.json',
                update: 'updatePersons',
                destroy: 'destroyPersons'
            }
        },     
        
        lazyFill: true,
    }),
    

    
    
    
});