<!DOCTYPE html>
<html>
<head>
<title>Matches</title>

<style>
body {
    font-family: 'Segoe UI';
    background: linear-gradient(to right, #00b09b, #96c93d);
    text-align: center;
    padding: 30px;
}

h1 {
    color: white;
}

.card {
    background: white;
    padding: 20px;
    margin: 15px auto;
    width: 300px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    text-align: left;
}

.no-match {
    color: white;
    margin-top: 20px;
    font-size: 18px;
}
</style>

</head>

<body>

<h1>🤝 Matching Profiles</h1>

{% if matches and matches|length > 0 %}

    {% for match in matches %}
    <div class="card">
        <h3>{{ match.name }}</h3>
        <p><b>Email:</b> {{ match.email }}</p>
        <p><b>Has:</b> {{ match.have }}</p>
        <p><b>Wants:</b> {{ match.want }}</p>
    </div>
    {% endfor %}

{% else %}

    <p class="no-match">No matches found yet 😕</p>

{% endif %}

</body>
</html>