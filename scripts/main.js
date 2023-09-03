var set_hiding = null;
var set_locked = false;

var hidden = [];

function onExpand(tree, show = false)
{
	var e = document.getElementById(tree);
	if (e == null) return;

	if (e.className == 'hide')
	{
		e.className = 'off';
		setTimeout(function()
		{
			const i = hidden.indexOf(tree);
			if (i != -1) hidden.splice(i, 1);

			e.className = 'on';
		}, 150);
	}
	else if (!show)
	{
		e.className = 'off';
		setTimeout(function()
		{
			const i = hidden.indexOf(tree);
			if (i == -1) hidden.push(tree);

			e.className = 'hide';
		}, 1000);
	}
}

function onError(code)
{
	var msg = 'Wystąpił błąd';

	if (errors.hasOwnProperty(code))
		msg = errors[code];

	showToast(msg, 5000);
	set_locked = false;
}

function onDone(code)
{
	var msg = 'Wykonano zapytanie';

	if (dones.hasOwnProperty(code))
		msg = dones[code];

	showToast(msg, 5000);
	set_locked = false;
}

function onMessage(msg)
{
	showToast(msg, 5000);
	set_locked = false;
}

function onLogout()
{
	if (set_locked) return;
	else set_locked = true;

	$.when($.get('logout.var'))
	.done(function(msg)
	{
		showToast(msg);
		makeRedirect('/');
	})
	.fail(function(msg)
	{
		if (!msg.hasOwnProperty('responseText')) onError('');
		else onMessage(msg.responseText);
	});
}

function makeRedirect(to, time = 3000)
{
	if (time <= 0) window.location.replace(to);
	else setTimeout(function()
	{
		window.location.replace(to);
	}, time);
}

function genItem(f, c, t, n, req = false)
{
	var i = document.createElement(c);

	i.type = t;
	i.name = n;
	i.id = n;
	i.required = req;

	f.append(i);

	return i;
}

function genLabel(f, t, p = null, n = null)
{
	var i = document.createElement('label');

	if (p) i.htmlFor = p;
	if (n) i.id = n;

	i.innerText = t;
	f.append(i);

	return i;
}

function genHash(string)
{
	var hash = 0;
	if (string.length == 0) return hash;

	for (let i = 0; i < string.length; i++)
	{
		var charCode = string.charCodeAt(i);

		hash = ((hash << 7) - hash) + charCode;
		hash = hash & hash;
	}

	return hash;
}

function checkLogon()
{
	$.when($.get('islogon.var'))
	.done(function(msg)
	{
		var obj = document.getElementById('logout');

		if (msg == "False") obj.style.display = "none";
	})
}

function showToast(msg, time = 5000)
{
	var x = document.getElementById('toast');

	clearTimeout(set_hiding);
	x.innerHTML = msg;
	x.className = 'show';

	if (time)
	{
		set_hiding = setTimeout(function()
		{
			x.className = 'hide';

			setTimeout(function()
			{
				x.className = '';
			}, 1000);
		}, time);
	}
}

function hideToast()
{
	var x = document.getElementById('toast');

	clearTimeout(set_hiding);
	x.innerHTML = msg;
	x.className = 'hide';

	setTimeout(function()
	{
		x.className = '';
	}, 1000);
}
