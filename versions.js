arr = window.location.href.split('/');
page = arr[arr.length - 1];
document.write('\
<dl>\
    <dt>Versions</dt> \
    <dd><a href="../master/' + page + '">master</a></dd>\
    <dd><a href="../4.2/' + page + '">4.2</a></dd>\
    <dd><a href="../4.1/' + page + '">4.1</a></dd>\
    <dd><a href="../4.0.1/' + page + '">4.0.1</a></dd>\
    <dd><a href="../4.0.0/' + page + '">4.0.0</a></dd>\
</dl>\
');