
// pass in a django {% url %} with 1234599 as the field. Pass in the table row class.
// Call this from JS at end.
function addClickHandlers(template, row_class) {
    // Add onclick to each row so that it leaps off to the detail
    for (const row of document.getElementsByClassName(row_class)) {
        var id = row.getAttribute('data-id');
        let url = template.replace(/1234599/, id.toString());
        row.addEventListener("click", function() {
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

function pageY(elem) {
    return elem.offsetParent ? (elem.offsetTop + pageY(elem.offsetParent)) : elem.offsetTop;
}

// for each table, the struct is <div dtalt><div table-structure><table><nav></div></div>
// if you make the inner div scrollable, the pagination gets scrolled.
// so we insert a new div:
// <div dtalt><div tabstruct><nav stuff></div><div scrollable><table></div></div>
// then the scrollable one can be...made scrollable
function insertScrollableDivs(applyHandlers=false) {
    for (const outerTableDiv of document.getElementsByClassName('scrollify-me')) {
        const innerTable = outerTableDiv.getElementsByTagName("table")[0];
        innerTable.remove();

        const newScrollableDiv = document.createElement('div');
        newScrollableDiv.className = "scrollable-div";
        newScrollableDiv.append(innerTable);
        outerTableDiv.insertBefore(newScrollableDiv, outerTableDiv.firstChild);
    }

    if (applyHandlers) {
        var resizeableTableDiv;
        const tableDivs = document.getElementsByClassName('expando-table');
        if (tableDivs.length) {
            resizeableTableDiv = tableDivs[0]
        } else {
            const scrollableDivs = document.getElementsByClassName('scrollable-div');
            if (scrollableDivs.length) {
                resizeableTableDiv = scrollableDivs[0]
            }
        }
        if (resizeableTableDiv) {
            const myDiv = resizeableTableDiv;
            const innerTable = myDiv.getElementsByTagName("table")[0];
            resize_function = function () {
                const buffer = 25 + 50; // scroll bar buffer + nav button buffer
                var height = document.documentElement.clientHeight;
                height -= pageY(myDiv) + buffer;
                height = (height < 0) ? 0 : height;
                if (innerTable.offsetHeight < height) {
                    myDiv.style.height = innerTable.offsetHeight + 'px';
                } else {
                    myDiv.style.height = height + 'px';
                }
            }
            window.addEventListener('resize', resize_function);
            // resize_function();
            return resize_function;
        }
    }
    return 0;
}


