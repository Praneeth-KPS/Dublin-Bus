let map;
    
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: {lat: 53.350140, lng: -6.266155},
    });

    const transitLayer = new google.maps.TransitLayer();
    transitLayer.setMap(map);

    var FromInput = document.getElementById('txtFrom');
    var ToInput = document.getElementById('txtTo');

    map.controls[google.maps.ControlPosition.TOP_LEFT].push(FromInput);
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(ToInput);
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
    autocompleteStart.addListener('place_changed', function(){
        var place = autocompleteStart.getPlace();
        val = place.formatted_address; 
        
        if(!place.geometry || !place.geometry.location){
            document.getElementById("txtFrom").value = 'No such results';
        }
        else{
            document.getElementById("txtFrom").value = val;
            markerStart.setPosition(place.geometry.location);
            markerStart.setVisible(true);
            StartCoord.lat = markerStart.getPosition().lat();
            StartCoord.lng = markerStart.getPosition().lng();
            calculateAndDisplayRoute(directionsService, directionsDisplay);
        }
    });
    autocompleteEnd.addListener('place_changed', function(){
        var place = autocompleteEnd.getPlace();
        const val = place.formatted_address; 
        

        if(!place.geometry || !place.geometry.location){
            document.getElementById("txtTo").value = 'No such results';
        }
        else{
            document.getElementById("txtTo").value = val;
            markerEnd.setPosition(place.geometry.location);
            markerEnd.setVisible(true);
            EndCoord.lat = markerEnd.getPosition().lat();
            EndCoord.lng = markerEnd.getPosition().lng();
            calculateAndDisplayRoute(directionsService, directionsDisplay);
        }
    });

    google.maps.event.addListener(markerStart, 'dragend', function(evt){
        StartCoord.lat = evt.latLng.lat();
        StartCoord.lng = evt.latLng.lng();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    });

    google.maps.event.addListener(markerEnd, 'dragend', function(evt){
        EndCoord.lat = evt.latLng.lat();
        EndCoord.lng = evt.latLng.lng();
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    });

    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;

    directionsDisplay.setMap(map);
    directionsDisplay.setOptions( { suppressMarkers: true } );

    var onChangeHandler = function(){
        calculateAndDisplayRoute(directionsService, directionsDisplay);
    };
    document.getElementById('RoutingPreference').addEventListener('change', onChangeHandler);
    
    function calculateAndDisplayRoute(directionsService, directionsDisplay){
        UserPreference = document.getElementById('RoutingPreference').value;
        console.log(UserPreference);
        if(UserPreference == 'Select'){
            UserPreference = 'FEWER_TRANSFERS';
        }
        console.log(UserPreference);
        let request = {
            origin: StartCoord,
            destination: EndCoord,
            travelMode: 'TRANSIT',
            transitOptions: {
                modes: ['BUS','RAIL','TRAIN','TRAM'],
                routingPreference: UserPreference,
              },
            // unitSystem: google.maps.UnitSystem.IMPERIAL,
        };
        directionsService.route(request, function(response, status) {
            if(status === 'OK') {
                directionsDisplay.setDirections(response);
            }else{
                window.alert('No route available between these stops');
            }
        });
        CalculateDistance();
    }

    function CalculateDistance(){
        var service = new google.maps.DistanceMatrixService();
        service.getDistanceMatrix(
            {
                origins: [StartCoord],
                destinations: [EndCoord],
                travelMode: google.maps.TravelMode.TRANSIT,
                transitOptions: {
                    modes: ['BUS','RAIL','TRAIN','TRAM'],
                    routingPreference: UserPreference,
                },
                unitSystem: google.maps.UnitSystem.metric,

            }, callback);
    }

    function callback(response, status){
        if(status != google.maps.DistanceMatrixStatus.OK){
            console.log('error');
        }
        else{
            var origin = response.originAddresses[0];
            var destination = response.destinationAddresses[0];
            if(response.rows[0].elements[0].status == 'ZERO_RESULTS'){
                console.log('No roads between origin and destination');
            }
            else{
                var distance = response.rows[0].elements[0].distance;
                var duration = response.rows[0].elements[0].duration;
                var distance_in_kilo = distance.value/1000;
                var distance_in_mile = distance.value/1609.34;
                var duration_text = duration.text;
                var duration_value = duration.value;
                document.getElementById('Distance').innerHTML = 'Distance in km : '+distance_in_kilo.toFixed(2)+' km';
                document.getElementById('TripTime').innerHTML = 'Trip Time : '+duration_text;
                // console.log(distance_in_mile.toFixed(2));
                // console.log(distance_in_kilo.toFixed(2));
                // console.log(duration_text);
                // console.log(duration_value);
                // console.log(origin);
                // console.log(destination);
            }
        }
    }

    //------------------------------------------------------------------------------
    // The below code is the alternate code for getting 3 markers near the destination.
    // but this will return only 1 closest marker. hence we switched to google spherical library


    // function rad(x) {return x*Math.PI/180;}
    // function find_closest_markers() {
    //     var lat = EndCoord.lat;
    //     var lng = EndCoord.lng;
    //     var R = 6371; // radius of earth in km
    //     var distances = [];
    //     var closest = -1;
    //     for( i=0;i<All_BikeMarkers.length; i++ ) {
    //         var mlat = All_BikeMarkers[i].position.lat();
    //         var mlng = All_BikeMarkers[i].position.lng();
    //         var dLat  = rad(mlat - lat);
    //         var dLong = rad(mlng - lng);
    //         var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    //             Math.cos(rad(lat)) * Math.cos(rad(lat)) * Math.sin(dLong/2) * Math.sin(dLong/2);
    //         var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    //         var d = R * c;
    //         distances[i] = d;
    //         if ( closest == -1 || d < distances[closest] ) {
    //             closest = i;
    //         }
    //     }

    //     alert(All_BikeMarkers[closest].title);
    // }

    //---------------------------------------------------------------------------------
    // The below is to get all the bus stations and plot a marker for each station on the map.
    // i tried to plot a polytline between all the stations but it gives overlimit error
    // As total stations are around 4k but the daily limit of the api is 2500. Hence not able to draw polyline.


    // var Markers = [];
    // var AllStops = [];
    // BusStops.forEach(stop =>{
    //     var BusCoord = {lat: parseFloat(stop.Latitude), lng: parseFloat(stop.Longitude)};        
    //     const marker = new google.maps.Marker({
    //         position: BusCoord,
    //         map: map
    //     });
    //     Markers.push(marker);
    //     AllStops.push(BusCoord);
    // });

    // var line= new google.maps.Polyline({
    //     path: AllStops,
    //     geodesic: true,
    //     strokeColor: '#FF0000',
    //     strokeOpacity: 1.0,
    //     strokeWeight: 2
    // });

    // line.setMap(map);
    // var delayFactor = 0;
    // var service = new google.maps.DirectionsService();

    // function DirectionsRoute(request){
    //     service.route(request, function(result, status) {
    //         if (status == google.maps.DirectionsStatus.OK) {

    //             //Initialize the Path Array
    //             var path = new google.maps.MVCArray();
    //             //Set the Path Stroke Color
    //             var poly = new google.maps.Polyline({
    //             map: map,
    //             strokeColor: '#4986E7'
    //             });
    //             poly.setPath(path);
    //             for (var i = 0, len = result.routes[0].overview_path.length; i < len; i++) {
    //                  path.push(result.routes[0].overview_path[i]);
    //             }
    //         }
    //         else if (status === google.maps.DirectionsStatus.OVER_QUERY_LIMIT) {
    //             delayFactor++;
    //             setTimeout(function () {
    //                 DirectionsRoute(request);
    //             }, delayFactor * 10000);
    //         } 
    //         else {
    //             console.log("Route: " + status);
    //         }
    //     });
    // }

    // //Loop and Draw Path Route between the Points on MAP
    // for (var i = 0; i < AllStops.length; i++) {
    //     if ((i + 1) < AllStops.length) {
    //         var src = AllStops[i];
    //         var des = AllStops[i + 1];

    //         var request = {
    //         origin: src,
    //         destination: des,
    //         travelMode: google.maps.DirectionsTravelMode.WALKING
    //         };
    //         DirectionsRoute(request);
    //     }
    // }
}

