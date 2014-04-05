var srvsay = function() {
    Dajaxice.minecraft.server_say(
            Dajax.process,
            {
                'server_pk':{{ server.pk }},
                'message':$("#tosay").val()
                }
            );
    //$("#tosay").val("");
};

var forEnter = function(event) {
    if (event.which == 13 || event.keyCode == 13) {
        event.preventDefault();
        srvsay();
    };
};

