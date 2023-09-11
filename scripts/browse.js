const errors =
{
	'range': 'Wskazana strona nie istnieje',
	'load': 'Nie udało się wczytać listy folderów',
	'get': 'Nie udało się otworzyć folderu'
};

const MAX_LIST = 50;

function onLoad()
{
	$.ajaxSetup({ 'timeout': 5000 });

	const dirId = getParam('dir');
	const docId = getParam('doc');

	if (dirId) $.when($.getJSON(`/getlist.var?id=${dirId}`, onFilelist)).fail(showLoadFail);
	else if (docId) $.when($.getJSON(`/getdoc.var?id=${dirId}`, onFileshow)).fail(showLoadFail);
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

	const add = document.createElement('a');
	add.href = `/append.html?dir=${id}`;
	add.text = '+';

	cols[0].appendChild(ref);
	cols[1].innerText = count;
	cols[2].appendChild(add);

	parent.appendChild(row);
	row.id = `dir_${id}`;
}

function onFilelist(data)
{
	const heads = [ "Nazwa", "Status", "Utworzony", "Dodany", "Zmodyfikowany" ];

	const list = document.getElementById('list');
	const page = document.getElementById('page');

	const tab = document.createElement('table');
	const row = document.createElement('tr');

	var pageId = getParam('page');

	if (pageId > 0) --pageId;
	else pageId = 0;

	list.innerHTML = '';
	page.innerHTML = '';
	tab.id = 'tab';

	for (var i = 0; i < heads.length; ++i)
	{
		col = document.createElement('th');
		col.innerText = heads[i];
		row.appendChild(col);
	}

	if (data.length > MAX_LIST || true)
	{
		const pMax = Math.ceil(data.length / MAX_LIST);

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
		spin.value = pageId + 1;
		spin.onchange = function()
		{
			if (!spin.validity.valid) onError('range');
			else onFilepage(spin.value - 1, data, tab);
		}

		page.appendChild(prefix);
		page.appendChild(spin);
		page.appendChild(sufix);
	}

	tab.appendChild(row);
	list.appendChild(tab);

	onFilepage(pageId, data, tab);
}

function onFilepage(id, data, tab)
{
	while (tab.rows.length > 1) tab.deleteRow(1);

	for (var i = id*MAX_LIST; i < (id+1)*MAX_LIST && i < data.length; ++i)
	{
		const e = data[i]; appendFile(e[0], e[1], e[2], e[3], e[4], e[5], tab);
	}
}

function appendFile(id, name, status, d_cre, d_add, d_mod, parent)
{
	id = Number(id); if (Number.isNaN(id)) return;

	const row = document.createElement('tr');
	const sid = '[' + id + ']';
	const cols = [];

	for (var i = 0; i < 5; ++i)
	{
		cols[i] = document.createElement('td');
		row.appendChild(cols[i]);
	}

	const ref = document.createElement('a');
	ref.href = `/browse.html?doc=${id}`;
	ref.text = name;

	cols[0].appendChild(ref);
	cols[1].innerText = status;
	cols[2].innerText = d_cre;
	cols[3].innerText = d_add;
	cols[4].innerText = d_mod;

	parent.appendChild(row);
	row.id = `doc_${id}`;
}

function showLoadFail()
{
	onError('load');
}
