$(document).ready(function(){

    var userdata = {
        "project_folder": "",
        "shp_file": "",
        "dbf_file": "",
        "shx_file": "",
        "dbf_file": "",
        "constraints": [],
        "affected_area": "",
    };

    localStorage.setItem("userdata", JSON.stringify(userdata));

    // to be hidden
    $("#constrains").hide();
    $("#period").hide();
    $("#calibration").hide();
    $("#config").hide();

    // constraint management
    $("#constraint-show").click((ev) => {
        let all_c_code = "";
        userdata = JSON.parse(localStorage.getItem("userdata"));
        if(userdata.constraints.length > 0){
            for(let i=0; i<userdata.constraints.length; i++){
                let item = userdata.constraints[i];
                let constraint_code = "<div class='mt-2'>\
                        <label for='c"+i+"max'>Constraint "+i+" upper limit</label><br/>\
                        <input type='number' id='c"+i+"max' name='c"+i+"max' value='"+item.maximun+"'/>\
                    </div>\
                    <div class='mt-2'>\
                        <label for='c"+i+"min'>Constraint "+i+" lower limit</label><br/>\
                        <input type='number' id='c"+i+"min' name='c"+i+"min' value='"+item.minimun+"'/>\
                    </div>";
                all_c_code += constraint_code;
            }
            $("#constraints_conf").html(all_c_code);
            $("#constrains").show(400);
        }else{
            alert("Sorry you should provide constraints in main configuration first");
        }
    })

    $("#save_const").click(()=>{
        userdata = JSON.parse(localStorage.getItem("userdata"));
        if(userdata.constraints.length > 0){
            for(let i=0; i<userdata.constraints.length; i++){
                let max = parseFloat($("#c"+i+"max").val());
                let min = parseFloat($("#c"+i+"min").val());
                userdata.constraints[i].minimun = min;
                userdata.constraints[i].maximun = max;
            }
            localStorage.setItem("userdata", JSON.stringify(userdata));
            $("#constrains").hide(400);
        }
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
    });

    $("#config-form").submit(function(e){
        return false;
    });

    $("#save_configs").click((ev) => {
        userdata.project_folder = $("#pfolder").val();
        userdata.shp_file = $("#shp_file").val();
        userdata.dbf_file = $("#dbf_file").val();
        userdata.shx_file = $("#shx_file").val();
        let num_con = parseInt($("#num_cons").val());
        for(let i=0; i<num_con; i++){
            userdata.constraints.push({
                "file_path": $("#c"+i+"").val(),
                "minimun": 0,
                "maximun": 0,
            })
        }
        userdata.affected_area = $("#affected_area").val();
        localStorage.setItem("userdata", JSON.stringify(userdata));
        $("#config").hide(400);
    })

    var map = L.map('map').setView([51.505, -0.09], 13);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

})