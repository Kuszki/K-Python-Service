function onLoad()
{
	const info = document.getElementById('welcome');

	$.ajaxSetup({ 'timeout': 5000 });
	
	$.when($.get('/getuser.var'))
	.done(function(msg)
	{
		info.innerText = `Witaj ${msg}, aby rozpocząć pracę wybierz akcję z menu`;
	})
	.fail(function()
	{
		info.innerText = 'Witaj, aby rozpocząć pracę wybierz akcję z menu';
	});
}
