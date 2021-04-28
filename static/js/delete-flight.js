function searchFlights() {
    var sourceCity = document.form.src_city.value;
    var destCity = document.form.dest_city.value;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            renderData(this.responseText, sourceCity, destCity)
        }
    };
    var url = "get-flights?source_city=" + sourceCity + "&dest_city=" + destCity
    xhttp.open("GET", url, true);
    xhttp.send();
}

function renderData(reposnse, sourceCity, destCity) {
    var json = JSON.parse(reposnse);
    if (!json) {
        var item = `<div class="card text-white bg-danger list-group-item">
                <div class="card-header">Not available!</div>
                <div class="card-body">
                    <h5 class="card-title">No Flights available from ${sourceCity} to ${destCity}</h5>
                    <p class="card-text">Please check the route</p>
                    </div>
                    </div>`
        document.getElementById("searchResults").innerHTML = item;
        return;
    }
    var count = json.length;
    var html = ""
    for (let i = 0; i < count; i++) {
        var item = `<div class="card text-white bg-success list-group-item" >
  <h5 class="card-header">Flight ID: ${json[i].f_id}</h5>
  <div class="card-body">
    <h5 class="card-title">${sourceCity} to ${destCity}</h5>
    <p class="card-text">Departure Time: ${json[i].d_time} HRS<br>
        Arrival Time: ${json[i].a_time} HRS<br>
        Economy Class Ticket Cost: INR ${json[i].e_cost}<br>
        Business Class Ticket Cost: INR ${json[i].b_cost}</p>
    <a href="/remove?flight_id=${json[i]._id}" class="btn btn-primary bg-danger" >Delete</a>
  </div>
</div>`
        html += item;
    }
    document.getElementById("searchResults").innerHTML = html;
}