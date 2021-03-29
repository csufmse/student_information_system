
// pass in a django {% url %} with 1234599 as the field. Pass in the table row class.
// Call this from JS at end.
function addClickHandlers(template, row_class) {
    // Add onclick to each row so that it leaps off to the detail
    var tablerows = document.getElementsByClassName(row_class)
    for (var i = 0, len = tablerows.length; i < len; i = i + 1) {
        var row = tablerows[i];
        row.addEventListener("click", function() {
            var id = row.getAttribute('data-id');
            var url = template.replace(/1234599/, id.toString());
            open(url,'_self');
        }, false);
    }
}

function addButtonClickHandler(button_id, url) {
    // Add onclick to each row so that it leaps off to the detail
    var btn = document.getElementById(button_id)
    if ( !btn ) {
        console.log("ERROR: unable to attach click to button "+button_id);
    } else {
        btn.addEventListener("click", function () {
            open(url, '_self');
        }, false);
    }
}

// Change the empty label for min/max range filters
function stylizeRange({field=0, name=0, min_label=0,
                          max_label=0, width='90px'}) {
    var label0;
    var label1;
    if (name) {
        label0 = "Min "+name;
        label1 = "Max "+name;
    }
    else {
        if (min_label) {
            label0 = min_label;
        }
        if (max_label) {
            label1 = max_label;
        }
    }
    var e;
    e = document.getElementById('id_'+field+'_0');
    e.placeholder = label0;
    e.style.width = width;
    e = document.getElementById('id_'+field+'_1');
    e.placeholder = label1;
    e.style.width = width;
}



