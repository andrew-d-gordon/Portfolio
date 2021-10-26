//GET request to find if a place exists in Mongo using placeid as identifier, returns rating
function findPlaceRating(place, cuisineType) {
    fetch("https://delish-food-292917.appspot.com/" + place.place_id)
        .then(response => response.json())
        //place found, creating marker with rating
        .then(
            data => {
                createMarker(place, cuisineType, data.rating)
            }
        )
        //place not found, add place to mongo and create marker for new place
        .catch((error) => {
            addPlace(place.place_id)
            createMarker(place, cuisineType, 0)
        })
}

//POST request to add place to mongoDB
function addPlace(goog_id) {
    const url = "https://delish-food-292917.wl.r.appspot.com/add-doc";
    const data = { "placeid": goog_id };

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .catch((error) => {
            console.error("Error:", error)
        });
}

function updateRating(placeid, voteVal) {
    alert(`${voteVal} recorded!`);
    const url = "https://delish-food-292917.appspot.com/" + voteVal.toLowerCase();
	var data = {"placeid": placeid};

    fetch(url, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .catch((error) => {
        console.error("Error:", error)
    });
}