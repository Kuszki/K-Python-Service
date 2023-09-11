const errors =
{
	'empty': 'Wprowadź nazwę użytkownika oraz hasło',
	'login': 'Nie udało się zalogować do systemu'
};

function onLoad()
{
	$.ajaxSetup({ 'timeout': 5000 });

	$.when($.get('/getuser.var'))
	.done(function(msg)
	{
		const user = document.getElementById('user');

		user.value = msg;
		user.readOnly = true;
	})

	$("#login").on("submit", function(event)
	{
  		event.preventDefault();
  		onLogin();
	});
}

function onLogin()
{
	if (set_locked) return;

	const submit = document.getElementById('submit');
	const user = document.getElementById('user').value;
	const pass = document.getElementById('pass').value;

	if (user == '' || pass == '')
	{
		onError('empty'); return;
	}
	else
	{
		set_locked = true;
	}

	data =
	{
		'user': user,
		'pass': pass
	};

	$.when($.ajax(
	{
		'url': '/logon.var',
		'type': 'POST',
		'contentType': 'application/json',
		'data': JSON.stringify(data)
	}))
	.done(function(msg)
	{
		showToast(msg);
		makeRedirect();
	})
	.fail(function(msg)
	{
		if (!msg.hasOwnProperty('responseText')) onError('login');
		else onMessage(msg.responseText);
	});
}
