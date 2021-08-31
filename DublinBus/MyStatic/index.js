let map;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 53.350140, lng: -6.266155 },
    });

    const transitLayer = new google.maps.TransitLayer();
    transitLayer.setMap(map);

    var FromInput = document.getElementById('txtFrom');
    var ToInput = document.getElementById('txtTo');

    // map.controls[google.maps.ControlPosition.TOP_LEFT].push(FromInput);
    // map.controls[google.maps.ControlPosition.TOP_LEFT].push(ToInput);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(document.getElementById('RoutingPreference'));

    var StartIcon = {
        url: "/static/Images/StartMarker.png",
        scaledSize: new google.maps.Size(60, 70),
    };

    var EndIcon = {
        url: "/static/Images/EndMarker.png",
        scaledSize: new google.maps.Size(60, 70),
    };

    var StartCoord = {
        lat: 53.306816,
        lng: -6.222995
    };

    var EndCoord = {
        lat: 53.343165294,
        lng: -6.256165642
    };

    markerStart = new google.maps.Marker({
        position: StartCoord,
        map: map,
        title: 'Start',
        draggable: true,
        visible: true,
        icon: StartIcon,
    });

    markerEnd = new google.maps.Marker({
        position: EndCoord,
        map: map,
        title: 'End',
        draggable: true,
        visible: true,
        icon: EndIcon,
    });


    // Guinness Storehouse Marker
    var guinnessCoord = {
        lat: 53.3420,
        lng: -6.2867
    };

    var activityMarker = {
        url: "/static/Images/map_marker.png",
        scaledSize: new google.maps.Size(25, 45),
    };

    guinnessStorehouse = new google.maps.Marker({
        position: guinnessCoord,
        map: map,
        title: 'The Guinness Storehouse',
        icon: activityMarker
    });

    guinnessStorehouse.addListener("click", () => {
        if (windowOpen) {
            windowOpen.close();
        }
        const infowindow = new google.maps.InfoWindow({
            content: "<img src='/static/Images/guinness.jpg' alt='The Guinness Storehouse' width='450' height='210'>"
                + "<div class='card' style='width: 18rem;'>"
                + "<img class='card-img-top' src='/static/Images/guinness.jpg' alt='The Guinness Storehouse'>"
                + "<div class='card-body'>"
                + "<h5 class='The Guinness Storehouse'>The Guinness Storehouse</h5>"
                + "<p class='card-text'><b>Description: </b>Explore the story of Guinness before taking in the views of Dublin from the Gravity Bar while enjoying your perfectly poured, perfectly chilled pint of Guinness, included in your ticket.</p>"
                + "<a href='https://www.guinness-storehouse.com/en' class='btn btn-primary' target='_blank'>More Information</a>"
                + "</div></div>",
            // maxWidth: 450
        });
        windowOpen = infowindow;
        infowindow.open(map, guinnessStorehouse);
    });

    // End of Guinness hard-coded addition



    var defaultBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(52.999804, -6.841221),
        new google.maps.LatLng(53.693350, -5.914248));

    var options = {
        bounds: defaultBounds,
        strictBounds: true,
    };

    autocompleteStart = new google.maps.places.Autocomplete(FromInput, options);
    autocompleteEnd = new google.maps.places.Autocomplete(ToInput, options);

    // Update values of the search bar instantly when a new place is chosen
    autocompleteStart.addListener('place_changed', function () {
        var place = autocompleteStart.getPlace();
        val = place.formatted_address;

        if (!place.geometry || !place.geometry.location) {
            document.getElementById("txtFrom").value = 'No such results';
        }
        else {
            document.getElementById("txtFrom").value = val;
            markerStart.setPosition(place.geometry.location);
            markerStart.setVisible(true);
            StartCoord.lat = markerStart.getPosition().lat();
            StartCoord.lng = markerStart.getPosition().lng();
            calculateAndDisplayRoute(directionsService, directionsDisplay);
        }
    });
    autocompleteEnd.addListener('place_changed', function () {
        var place = autocompleteEnd.getPlace();
        const val = place.formatted_address;


        if (!place.geometry || !place.geometry.location) {
            document.getElementById("txtTo").value = 'No such results';
        }
        else {
            document.getElementById("txtTo").value = val;
            markerEnd.setPosition(place.geometry.location);
            markerEnd.setVisible(true);
            EndCoord.lat = markerEnd.getPosition().lat();
            EndCoord.lng = markerEnd.getPosition().lng();
            calculateAndDisplayRoute(directionsService, directionsDisplay);
        }
    });

    google.maps.event.addListener(markerStart, 'dragend', function (evt) {
        StartCoord.lat = evt.latLng.lat();
        StartCoord.lng = evt.latLng.lng();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    });

    google.maps.event.addListener(markerEnd, 'dragend', function (evt) {
        EndCoord.lat = evt.latLng.lat();
        EndCoord.lng = evt.latLng.lng();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    });

    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;

    directionsDisplay.setMap(map);
    directionsDisplay.setOptions({ suppressMarkers: true });

    var onChangeHandler = function () {
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    };
    document.getElementById('RoutingPreference').addEventListener('change', onChangeHandler);

    function calculateAndDisplayRoute(directionsService, directionsDisplay) {
        UserPreference = document.getElementById('RoutingPreference').value;
        console.log(UserPreference);
        if (UserPreference == 'Select') {
            UserPreference = 'FEWER_TRANSFERS';
        }
        console.log(UserPreference);
        let request = {
            origin: StartCoord,
            destination: EndCoord,
            travelMode: 'TRANSIT',
            transitOptions: {
                modes: ['BUS', 'RAIL', 'TRAIN', 'TRAM'],
                routingPreference: UserPreference,
            },
            // unitSystem: google.maps.UnitSystem.IMPERIAL,
        };
        directionsService.route(request, function (response, status) {
            if (status === 'OK') {
                directionsDisplay.setDirections(response);
            } else {
                window.alert('No route available between these stops');
            }
        });
        CalculateDistance();
    }

    function CalculateDistance() {
        var service = new google.maps.DistanceMatrixService();
        service.getDistanceMatrix(
            {
                origins: [StartCoord],
                destinations: [EndCoord],
                travelMode: google.maps.TravelMode.TRANSIT,
                transitOptions: {
                    modes: ['BUS', 'RAIL', 'TRAIN', 'TRAM'],
                    routingPreference: UserPreference,
                },
                unitSystem: google.maps.UnitSystem.metric,

            }, callback);
    }

    function callback(response, status) {
        if (status != google.maps.DistanceMatrixStatus.OK) {
            console.log('error');
        }
        else {
            var origin = response.originAddresses[0];
            var destination = response.destinationAddresses[0];
            if (response.rows[0].elements[0].status == 'ZERO_RESULTS') {
                console.log('No roads between origin and destination');
            }
            else {
                var distance = response.rows[0].elements[0].distance;
                var duration = response.rows[0].elements[0].duration;
                var distance_in_kilo = distance.value / 1000;
                var distance_in_mile = distance.value / 1609.34;
                var duration_text = duration.text;
                var duration_value = duration.value;
                document.getElementById('Distance').innerHTML = 'Distance in km : ' + distance_in_kilo.toFixed(2) + ' km';
                document.getElementById('TripTime').innerHTML = 'Trip Time : ' + duration_text;
                // console.log(distance_in_mile.toFixed(2));
                // console.log(distance_in_kilo.toFixed(2));
                // console.log(duration_text);
                // console.log(duration_value);
                // console.log(origin);
                // console.log(destination);
            }
        }
    }
}

