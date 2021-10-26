// Globals for index.js about map information
var map;
var service;
var infowindow;
var mapCenterPos = {lat: 0, lng:0};
var centerMarkerContainer = [];
var centerMarkerSize = {height: 28, width: 30};

function initMap() {

  //center of earth coords
  var startCenter = new google.maps.LatLng(0, 0, 0);

  // show popup when click on marker
  infowindow = new google.maps.InfoWindow();

  //create the map
  map = new google.maps.Map(document.getElementById("map"), {
    center: startCenter,
    zoom: 3,
    mapTypeControl: true,
    fullscreenControl: false,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_RIGHT
    }
  });

  var mapStyle = [ // sets up getting rid of equator and international date line
    {
      featureType: "administrative",
      elementType: "geometry",
      stylers: [
        { visibility: "off" }
      ]
    }
  ];

  // Initialize centerMarkerContainer
  initCenterMarker();

  //Style the map
  var styledMap = new google.maps.StyledMapType(mapStyle);
  map.mapTypes.set('myCustomMap', styledMap);
  map.setMapTypeId('myCustomMap');
  
  map.addListener("click", (e) => {
    mapCenterPos["lat"] = e.latLng.lat();
    mapCenterPos["lng"] = e.latLng.lng();
    placeMarkerAndPanTo(mapCenterPos, map);
  });

  //create the button to close discription
  const closeDescriptionButton = document.querySelectorAll('[data-close-button]') 
  const overlay = document.getElementById('overlay')

  closeDescriptionButton.forEach(button => {
    button.addEventListener('click', () => {
      const description = button.closest('.description')
      closeDescription(description)
    })
  })

  //button to close description
  function closeDescription(description) {
    if (description == null) return
    description.classList.add('active')
    overlay.classList.add('active')
    overlay.parentNode.removeChild(overlay)
    geoLocation()
  }

  //Geolocation to track user location
  function geoLocation() {

    infoWindow = new google.maps.InfoWindow();
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {

          //Initialize Marker Clusterer
          clusters();

          const pos = { //get User coordinaties 
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };

          // Set zoom, move to user location, place center marker
          map.setZoom(15);
          map.setCenter(pos);
          mapCenterPos = pos;

          placeMarkerAndPanTo(pos, map);

          // Open nav/menu bar by default, set menu button to be transparent on start
          setMenuTransition(0);
          openNav()

          //Call cuisineTypeListener to init menu search options
          cuisineTypeListener();
        },
        () => { // Enable Location not allowed
          handleLocationError(true, infoWindow, map.getCenter());
        }
      );
    } else {
      // Browser doesn't support Geolocation
      handleLocationError(false, infoWindow, map.getCenter());
    }
  }

  //Error function on geolocation failure 
  function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
      browserHasGeolocation
        ? "Error: The Geolocation service failed. Please enable your location."
        : "Error: Your browser doesn't support geolocation."
    );

    infoWindow.open(map);
  }
}

// Initialize center marker container with null marker
function initCenterMarker() {
  const centerMarker = new google.maps.Marker({map: map});
  centerMarkerContainer.push(centerMarker);
}

// Set new center, place user marker, pan to marker
function placeMarkerAndPanTo(latLng, map) {

  // Get rid of old center marker
  var oldCenterMarker = centerMarkerContainer.pop();
  oldCenterMarker.setMap(null);
  oldCenterMarker = null;

  // Sets new center marker image and attributes
  const centerMarkerImage = {
    url: `./MarkerIcons/centerMarker.png`,
    origin: new google.maps.Point(0, 0),
    anchor: new google.maps.Point(0, 0),
    scaledSize: new google.maps.Size(centerMarkerSize.width, centerMarkerSize.height),
  };

  const centerMarker = new google.maps.Marker({
    icon: centerMarkerImage,
    position: latLng,
    map: map,
  });

  // Add centerMarker to container, set new center position center for search queries
  centerMarkerContainer.push(centerMarker);
  map.panTo(latLng);
}

// DIV ELEMENT MOVEMENT SCRIPTS
/* Set the width of the side navigation to 250px and the left margin of the page content to 250px
  and add a black background color to body */
function openNav() { //Onclick, open the side navigator
  document.getElementById("mySidenav").style.width = "250px";
  document.getElementById("menu").style.opacity = "0";
  document.getElementById("box").style.marginLeft = "250px";
  document.getElementById("map").style.marginLeft = "250px";
  document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0, and the 
background color of body to white */
function closeNav() { //On close, close the side navigator
  setMenuTransition(1);
  document.getElementById("mySidenav").style.width = "0";
  document.getElementById("menu").style.opacity = "1";
  document.getElementById("box").style.marginLeft = "0";
  document.getElementById("map").style.marginLeft = "0";
  document.body.style.backgroundColor = "white";
}

// Set Menu button transition time
function setMenuTransition(transitionTime) {
  document.getElementById("menu").style.transition = `opacity ${transitionTime}s ease-out`;
}