$(document).ready(function(){

    // to be hidden
    $("#constrains").hide();
    $("#period").hide();
    $("#calibration").hide();

    // constraint management
    $("#constraint-show").click((ev) => {
        $("#constrains").show(400);
    })

    $("#constraint-dispose").click((ev) => {
        $("#constrains").hide(400);
    })

    $("#calibration-show").click((ev) => {
        $("#calibration").show(400);
    })

    $("#calibration-hide").click((ev) => {
        $("#calibration").hide(400);
    })

    $("#period-hide").click((ev) => {
        $("#period").hide(400);
    })

    $("#period-show").click((ev) => {
        $("#period").show(400);
    })

    var map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);


    console.log("script loaded...");
})