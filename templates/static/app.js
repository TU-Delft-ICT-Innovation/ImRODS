
Ext.override(Ext.data.request.Ajax, {
    openRequest: function (options) {
        var xhr = this.callParent(arguments);
        if (options.progress) {
            xhr.upload.onprogress = options.progress;
        }
        return xhr;
    }
});

Ext.tip.QuickTipManager.init();

Ext.application({
    name: 'iRods',    
    appFolder : '/static',
    autoCreateViewport: 'iRods.view.main.Main'
});


