// Open on click/set information for marker's info box
function setMarkerInfoBox (place, marker, websiteTag, placePhotoTag, rating) {
	const infowindow = new google.maps.InfoWindow();
	var addr = place.formatted_address.split(",");
	var params = [place, marker, websiteTag, placePhotoTag, rating];
	// Add event listener to marker and set information for infobox
	google.maps.event.addListener(marker, "click", function () {
		infowindow.setContent( //Contents of each infowindow for each pin
			"<div><strong>" +
			place.name +
			"<br>" + 
			`Rating: ${rating} ` + 
			`<img src="./Icons/upvote.png" onclick="updateRating('${place.place_id}', 'Upvote') "width="20" height="20" />` +
			" " +  
			`<img src="./Icons/downvote.png" onclick="updateRating('${place.place_id}', 'Downvote') "width="20" height="20" />` +
			"</strong><br>" +  
			addr[0] + 
			"<br>" + 
			addr[1] + ((addr[2] == null) ? "":", "+addr[2]) + 
			"<br>" +
			websiteTag +
			"<br>" +
			placePhotoTag +
			"</div>"
			);
		infowindow.open(map, this);
	});
}

// Retrieve place photo if it exists, return photo html tag for infobox
function getPlacePhoto(place) {
	let placePhotoTag = "";
	try {
		placePhotoTag = (place.photos[0].getUrl()) ? `<img src='${place.photos[0].getUrl()}' height = "100">`:placePhotoTag;
	}
	catch(e){}

	return placePhotoTag;
}

// Retrieve google search query for place, return search query html tag for infobox
function getPlaceSearchUrl(place) {
	// Format query portion for search url, replace spaces with '%20'
	restaurantSearchResult = `${place.name} ${place.formatted_address}`;
	restaurantSearchResultq = restaurantSearchResult.replace(/ /g, "%20");
	restaurantSearchResultoq = restaurantSearchResult.replace(/ /g, "+");

	let websiteTag = `<a href = "https://www.google.com/search?q=${restaurantSearchResultq}&oq=${restaurantSearchResultoq}" target= "_blank">` + "Restaurant Info" + "</a>";
	return websiteTag;
}

// Retrieve information about a specific place, via gmaps service.getDetails()
function setPlaceDetails(place, marker, rating) {
	
	// Initialize service object and desired details request for place
	const service = new google.maps.places.PlacesService(map);
	const request ={
		placeId: place.place_id,
		fields: ["photo", "icon", "website", "opening_hours", "utc_offset_minutes"],
	};

	// Initialize websiteTag for infobox to google search query for place
	var websiteTag = getPlaceSearchUrl(place);

	// Send request for place details with given request
	service.getDetails(request, (detailsRequest, status) =>{
		if (status === google.maps.places.PlacesServiceStatus.OK) {
			try { // If website is associated with place, overwrite default search query websiteTag for infobox
				placeWebsiteUrl = `<a href = "${detailsRequest.website}" target= "_blank">` + "Restaurant Info" + "</a>";
				websiteTag = (detailsRequest.website) ? placeWebsiteUrl:websiteTag;
			}
			catch(e) {}
		}

		// Set MarkerInfoBox with retrieved details about place
		var placePhotoTag = getPlacePhoto(place);
		setMarkerInfoBox(place, marker, websiteTag, placePhotoTag, rating);
	});
}