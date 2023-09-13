function onLoad()
{
	const obj_pagenum = document.getElementById('pagenum');
	const obj_folders = document.getElementById('folders');
	const obj_files = document.getElementById('files');
	const obj_preview = document.getElementById('preview');

	var val_pagenum = localStorage.getItem("itemsPerPage");
	var val_folders = localStorage.getItem("openDirNew");
	var val_files = localStorage.getItem("openFileNew");
	var val_preview = localStorage.getItem("showFilePrewiew");

	if (val_pagenum == null) val_pagenum = 50;
	if (val_folders == null) val_folders = 0;
	if (val_files == null) val_files = 1;
	if (val_preview == null) val_preview = 1;

	obj_pagenum.value = val_pagenum;
	obj_folders.value = val_folders;
	obj_files.value = val_files;
	obj_preview.value = val_preview;

	obj_pagenum.onchange = function(e) { onValueChange("itemsPerPage", e.target); };
	obj_folders.onchange = function(e) { onValueChange("openDirNew", e.target); };
	obj_files.onchange = function(e) { onValueChange("openFileNew", e.target); };
	obj_preview.onchange = function(e) { onValueChange("showFilePrewiew", e.target); };

	document.getElementById('prefs').onsubmit = function() { return false; };
}

function onValueChange(name, obj)
{
	if (obj.validity.valid) localStorage.setItem(name, Number(obj.value));
}
