//Run requests from cuisine type clicks
function cuisineTypeSearch(request, cuisineType) {

    //hit the gmaps places API and do a text search
    var service = new google.maps.places.PlacesService(map);
    service.textSearch(request, callback);

    //parse returned info from places and either add or find place
    function callback(results, status) {
        if (status == google.maps.places.PlacesServiceStatus.OK) {
            for (var i = 0; i < results.length; i++) {
                var place = results[i];
                findPlaceRating(place, cuisineType);
            }
        }
    }
}

// Marker Size Attributes
var minimumMarkerSize = 25;
var maximumMarkerSize = 70;
var baseMarkerSize = 35;

// Create marker with custom size
function createMarker(place, cuisineType, rating) {
    // Set size for marker based on rating/min or max val
    let candidateSize = baseMarkerSize+rating;
    markerSize = Math.max(minimumMarkerSize, Math.min(candidateSize, maximumMarkerSize));

    // Sets custom image attributes
    const image = {
        url: `./MarkerIcons/${cuisineType}.png`,
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(0, 0),
        scaledSize: new google.maps.Size(markerSize, markerSize),
    };

    const marker = new google.maps.Marker({
        map,
        icon: image,
        title: place.name,
        position: place.geometry.location,
    });

    // Set place information when marker is clicked
    setPlaceDetails(place, marker, rating);

    // add generated marker to dictionary and clusterer set
    cuisine_marker_dict[cuisineType].push(marker);
    markerClusterer.addMarker(marker);
}

// Marker Clusterer object
var markerClusterer = null;

// Initialize markerClusterer Object
function clusters() {
    markerClusterer = new MarkerClusterer(map, cuisine_marker_dict, {
        imagePath: "https://unpkg.com/@googlemaps/markerclustererplus@1.0.3/images/m",
    });
    markerClusterer.setMinimumClusterSize(5);
}

// Clear specified set of markers from the map
function clearMarkerSets(cuisineType) {
    if (markerClusterer) {
        markerClusterer.removeMarkers(cuisine_marker_dict[cuisineType]);
    }   
}

// Individual cuisine marker dict/hash table to store marker arrays
var cuisine_marker_dict = {};

// Initialize onclick event listener for cuisine type options
function cuisineTypeListener() {

    let mysidenav = document.getElementById("mySidenav");
    let cuisines = mysidenav.querySelectorAll('a.cuisine-type');

    for (let i = 0; i < cuisines.length; i++) { 
        let cuisine = cuisines[i]; // Select individual cuisine type

        let cuisineType = cuisine.innerText.toLowerCase();
        cuisine_marker_dict[cuisineType] = [];

        cuisine.onclick = function () {
            cuisine_check = document.getElementById(`${cuisine.innerText}`); // CSN-TYPE CHECK BOX DIV

            // IF CUISINE TYPE CLICKED ALREADY SELECTED, CLEAR SELECTION, ELSE, RUN REQUEST/CREATE MARKERS
            if (cuisine_check.innerHTML != "") {
                cuisine_check.innerHTML = "";
                clearMarkerSets(cuisineType);
            } else {
                let request = { //Create the request for searching 
                    location: new google.maps.LatLng(mapCenterPos["lat"], mapCenterPos["lng"], 14),
                    radius: "5",
                    type: "restaurant",
                    query: cuisine.innerText.toLowerCase(),
                };
                
                // Add default cuisine icon image next to listing in menu, then query search
                document.getElementById(cuisine.innerHTML).innerHTML = `<img src="./MarkerIcons/${cuisineType}.png" width="25" height="25"/>`;
                cuisineTypeSearch(request, cuisineType);

            }
        }
    }
}