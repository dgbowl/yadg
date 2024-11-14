arr = window.location.href.split('/');
page = arr[arr.length - 1];
document.write('\
<dl>\
    <dt>Versions</dt> \
    <dd><a href="../main/' + page + '">main</a></dd>\
    <dd><a href="../6.0/' + page + '">6.0</a></dd>\
    <dd><a href="../5.1/' + page + '">5.1</a></dd>\
    <dd><a href="../5.0/' + page + '">5.0</a></dd>\
    <dd><a href="../4.2/' + page + '">4.2</a></dd>\
    <dd><a href="../4.1/' + page + '">4.1</a></dd>\
    <dd><a href="../4.0.1/' + page + '">4.0.1</a></dd>\
    <dd><a href="../4.0.0/' + page + '">4.0.0</a></dd>\
</dl>\
');