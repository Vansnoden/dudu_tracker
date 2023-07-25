$(document).ready(function(){

    var userdata = {
        "project_folder": "",
        "shp_file": "",
        "dbf_file": "",
        "shx_file": "",
        "dbf_file": "",
        "constraints": [],
    };

    // to be hidden
    $("#constrains").hide();
    $("#period").hide();
    $("#calibration").hide();

    console.log(userdata);

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

    $("#config-show").click((ev) => {
        $("#config").show(400);
    })

    $("#config-hide").click((ev) => {
        $("#config").hide(400);
    })

    $("#num_cons").change((ev) => {
        let num_cons = parseInt($("#num_cons").val());
        let all_c_code = "";
        for (let i=0; i<num_cons; i++){
            let constraint_code = "<div class='mt-2'>\
                <label for='c1'>Constraint "+i+"</label><br/>\
                <input type='file' id='c"+i+"' name='c"+i+"'/>\
            </div>";
            all_c_code += constraint_code;
        }
        $("#constraint_fields").html(all_c_code);
    })

    var map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

})