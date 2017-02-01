<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
	pageEncoding="ISO-8859-1"%>
<head>
<meta charset="ISO-8859-1">
<title>OneButton</title>
<link rel="stylesheet" type="text/css" href="./resource/css/header.css">
<link rel="stylesheet" type="text/css" href="./resource/css/body.css">
<!--Load the AJAX API-->
<script type="text/javascript"
	src="https://www.gstatic.com/charts/loader.js"></script>
<script type="text/javascript"
	src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
<script type="text/javascript">
	// Load the Visualization API and the corechart package.
	google.charts.load('current', {
		'packages' : [ 'corechart' ]
	});

	// Set a callback to run when the Google Visualization API is loaded.
	google.charts.setOnLoadCallback(drawChart);

	// Callback that creates and populates a data table,
	// instantiates the pie chart, passes in the data and
	// draws it.
	function drawChart() {
		var jsonData = '';
		$.ajax({
			url : "Demo",
			dataType : "json",
			async : false,
			success : function(data) {
				jsonData = data;
				setTimeout(function() {
					drawChart();
				}, 5000);
			}
		});
		// Create the data table.
		var data = new google.visualization.DataTable(jsonData);
		// Set chart options
		var options = {
			title : 'Cloud Sensor',
			titleTextStyle : {
				'color' : '#ffffff',
				'fontSize' : 27,
				'bold' : true
			},
			legend : {
				'textStyle' : {
					'color' : '#FFF'
				}
			},
			width : 500,
			height : 400,

			backgroundColor : '#000',
			is3D : true,
			vAxis : {
				'baselineColor' : '#fff',
				'textStyle' : {
					'color' : '#FFF',
					'bold' : true
				}
			}

		};

		// Instantiate and draw our chart, passing in some options.
		var chart = new google.visualization.BarChart(document
				.getElementById('chart_div'));
		chart.draw(data, options);
		//setTimeout(drawChart(), 6000);	
	}
</script>
</head>
<header>
	<h1>
		One<span>Button</span>
	</h1>
	<div class = "title">
		<ul>
			<li><a href="welcome.jsp">Welcome</a></li>
			<li><a href="button.jsp">Button</a></li>
			<li><a href="hub.jsp">Hub</a></li>
			<li class="dropdown"><a href="function.jsp" class="dropbtn">Function</a>
				<div class="dropdown-content">
					<a href="email.jsp">Sending Email</a>
				</div></li>
			<li><a href="demo.jsp">Demo</a></li>
		</ul>
	</div>
	<div class="sign">
		<%
			out.println("Hello " + session.getAttribute("Name"));
		%>
		<span>|</span><a href="Signout">Sign out</a>
	</div>
</header>
<body>
	<div id="chart_div"></div>
</body>
</html>