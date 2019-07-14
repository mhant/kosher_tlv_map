function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1); 
  var a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ; 
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
  var d = R * c; // Distance in km
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI/180)
}

function onLocation(position){
  var lat1 = position.coords.latitude;
  var long1 = position.coords.longitude;
  let closeEnough = [];
  
  for(let i=0; i < addresses.length; i++){
    let address = addresses[i];
    let distance = getDistanceFromLatLonInKm(lat1, long1, address.lat, address.lng);
    if (distance < 1.1) {
      closeEnough.push({distance: distance, info: address});
    }  
  }
  closeEnough.sort(function(a,b){return a.distance - b.distance;});
  var output =  document.getElementById('results');
  for(let i=0; i < closeEnough.length; i++){
    var current = closeEnough[i];
    var name = document.createTextNode(current.info.rest_name);
    var tr = document.createElement("tr");
    var td1 = document.createElement("td");
    td1.appendChild(name);
    var address = document.createTextNode(current.info.rest_addr);
    var td2 = document.createElement("td");
    td2.appendChild(address);
    let dist_string;
    if (current.distance<1){
      let dist = current.distance*1000;
      dist_string = parseInt(dist) + "m";
    }
    else{
      dist_string = current.distance.toPrecision(3) + "km";
    }
    var distance = document.createTextNode(dist_string);
    var td3 = document.createElement("td");
    td3.appendChild(distance);
    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);
    output.appendChild(tr);
  }
}

function findClose(){
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(onLocation);
  } else {
    alert("Location not available");
  }
}
