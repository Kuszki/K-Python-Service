const errors =
{
	'range': 'Wskazana strona nie istnieje',
	'load': 'Nie udało się wczytać zasobu'
};

const pages = {};
var perpage = 50;

var currPag = null;
var dirTarget = '_self';
var fileTarget = '_self';

function onLoad()
{
	$.ajaxSetup({ 'timeout': 15000 });

	const dirId = Number(getParam('dir'));
	const docId = Number(getParam('doc'));
	const itNum = Number(localStorage.getItem("itemsPerPage"));

	if (Number(localStorage.getItem("openDirNew"))) dirTarget = '_blank';
	if (Number(localStorage.getItem("openFileNew"))) fileTarget = '_blank';

	if (itNum > 0) perpage = Math.ceil(itNum);

	if (dirId) $.when($.getJSON(`/getcount.var?id=${dirId}`, onFilecount)).fail(showLoadFail);
	else if (docId) $.when($.getJSON(`/getdoc.var?id=${docId}`, onFileshow)).fail(showLoadFail);
	else $.when($.getJSON('/getlist.var', onDirlist)).fail(showLoadFail);
}

function onDirlist(data)
{
	const heads = [ "Nazwa", "Liczba obiektów", "Operacje" ];

	const list = document.getElementById('list');
	const page = document.getElementById('page');

	const tab = document.createElement('table');
	const row = document.createElement('tr');

	list.innerHTML = '';
	page.innerHTML = '';
	tab.id = 'tab';

	for (var i = 0; i < heads.length; ++i)
	{
		col = document.createElement('th');
		col.innerText = heads[i];
		row.appendChild(col);
	}

	tab.appendChild(row);
	list.appendChild(tab);

	for (const e of data) appendDir(e[0], e[1], e[2], tab);
}

function appendDir(id, name, count, parent)
{
	id = Number(id); if (Number.isNaN(id)) return;

	const row = document.createElement('tr');
	const sid = '[' + id + ']';
	const cols = [];

	for (var i = 0; i < 3; ++i)
	{
		cols[i] = document.createElement('td');
		row.appendChild(cols[i]);
	}

	const ref = document.createElement('a');
	ref.href = `/browse.html?dir=${id}`;
	ref.text = name;
	ref.target = dirTarget;

	const add = document.createElement('a');
	add.href = `/append.html?dir=${id}`;
	add.text = '+';

	cols[0].appendChild(ref);
	cols[1].innerText = count;
	cols[2].appendChild(add);

	parent.appendChild(row);
	row.id = `dir_${id}`;
}

function onFilecount(data)
{
	const list = document.getElementById('list');
	const page = document.getElementById('page');

	var pageId = Number(getParam('page'));
	var dirId = Number(getParam('dir'));

	if (isNaN(pageId)) pageId = 1;
	else pageId = Math.max(1, pageId);

	const count = Number(data);
	const pMax = Math.ceil(count / perpage);

	const prefix = document.createElement('text');
	prefix.innerText = 'Strona ';

	const sufix = document.createElement('text');
	sufix.innerText = ` z ${pMax}`;

	const spin = document.createElement('input');
	spin.id = 'spin';
	spin.class = 'page'
	spin.type = 'number';
	spin.min = 1;
	spin.max = pMax;
	spin.value = pageId;
	spin.onchange = function()
	{
		if (!spin.validity.valid) onError('range');
		else onPagechange(spin.value, dirId, perpage, spin, list);
	}

	page.innerHTML = '';
	page.appendChild(prefix);
	page.appendChild(spin);
	page.appendChild(sufix);

	onPagechange(pageId, dirId, perpage, spin, list);
}

function onFilelist(data)
{
	const heads = [ "Nazwa", "Typ", "Status", "Utworzony", "Dodany", "Zmodyfikowany" ];

	const list = document.getElementById('list');

	const tab = document.createElement('table');
	const row = document.createElement('tr');

	var pageId = Number(getParam('page'));
	var dirId = Number(getParam('dir'));

	if (isNaN(pageId)) pageId = 1;
	else pageId = Math.max(1, pageId);

	for (var i = 0; i < heads.length; ++i)
	{
		col = document.createElement('th');
		col.innerText = heads[i];
		row.appendChild(col);
	}

	tab.id = 'tab';
	list.innerHTML = '';
	tab.appendChild(row);
	list.appendChild(tab);

	for (const e of data) appendFile(e, tab);
}

function appendFile(data, parent)
{
	const id = Number(data[0]); if (Number.isNaN(id)) return;

	const row = document.createElement('tr');

	const sid = '[' + id + ']';
	const cols = [];

	const ref = document.createElement('a');
	ref.href = `/browse.html?doc=${id}`;
	ref.text = data[1];
	ref.target = fileTarget;

	for (var i = 0; i < data.length - 1; ++i)
	{
		cols[i] = document.createElement('td');
		row.appendChild(cols[i]);

		if (i > 0) cols[i].innerText = data[i+1];
		else cols[i].appendChild(ref);
	}

	parent.appendChild(row);
	row.id = `doc_${id}`;
}

function onPagechange(id, dir, count, spin, tab)
{
	if (set_locked) return;

	const oldPag = currPag;

	if (id == currPag) return;
	else currPag = id;
	
	const url = `/browse.html?dir=${dir}&page=${id}&count=${count}`;

	if (pages.hasOwnProperty(id))
	{	
		window.history.replaceState(null, null, url);
		onFilelist(pages[id]);
	}
	else
	{
		spin.disabled = set_locked = true;
		tab.className = 'disabled';
		
		requestPage(dir, id, count, spin, tab, url);
	}
}

function requestPage(dir, id, count, spin, tab, url)
{
	const focus = document.activeElement == spin;

	$.when($.getJSON(`/getlist.var?id=${dir}&page=${id}&count=${count}`, function(data)
	{
		window.history.replaceState(null, null, url);
		onFilelist(pages[id] = data);
	}))
	.done(function()
	{
		spin.disabled = set_locked = false;
		tab.className = '';

		if (focus) spin.focus();
	})
	.fail(function(msg)
	{
		spin.disabled = set_locked = false;
		tab.className = '';
		
		showLoadFail(msg);
	});
}

function onFileshow(data)
{

}

function showLoadFail(msg)
{
	const list = document.getElementById('list'); onError('load');

	if (!msg.hasOwnProperty('responseText')) list.innerText = errors['load'];
	else list.innerText = errors['load'] + ": " + msg.responseText;
}
