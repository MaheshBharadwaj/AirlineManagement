function listRequests() {

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            renderData(this.responseText)
        }
    };
    xhttp.open("GET", "get-cancellations", true);
    xhttp.send();


}

function renderData(reposnse) {

    var json = JSON.parse(reposnse);
    if (!json || json.length == 0) {
        var item = `<div class="card text-white bg-success list-group-item">
                <div class="card-header">Not available!</div>
                <div class="card-body">
                    <h5 class="card-title">No Requests received!</h5>
                    
                    </div>
                    </div>`
        document.getElementById("searchResults").innerHTML = item;
        return;
    }

    var html = ""
    var count = json.length;
    for (let i = 0; i < count; i++) {
        var item = `<div class="card text-white list-group-item bg-info"  >
  <h5 class="card-header">User ID: ${json[i].email}</h5>
  <div class="card-body">
    <h5 class="card-title">${json[i].source_city} to ${json[i].dest_city}</h5>
    <p class="card-text">Departure Time: ${json[i].d_time} HRS<br>
        Arrival Time: ${json[i].a_time} HRS<br>`
        if (json[i].e_count != 0) {
            item += `Economy Class Tickets : ${json[i].e_count} Nos <br>`
        }
        if (json[i].b_count != 0) {
            item += `Business Class Tickets : ${json[i].b_count} Nos <br>`
        }
        item += `Date : ${json[i].date} <br>`

        item += `
            <br><a href="/handle-request?status=reject&c_id=${json[i]._id}" class="btn btn-primary bg-danger mr-3" >Reject Request</a><a href="/handle-request?status=approve&c_id=${json[i]._id}" class="btn btn-primary bg-success mr-3" >Approve Request</a>`
        item += `</p></div></div><br><br>`
    }
    html += item;
    document.getElementById("searchResults").innerHTML = html;
}