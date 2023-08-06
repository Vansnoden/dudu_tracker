async function postData(url = "", data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, *cors, same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, *same-origin, omit
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: "follow", // manual, *follow, error
        referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}

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

    var configForm = null;

    localStorage.setItem("userdata", JSON.stringify(userdata));

    // to be hidden
    $("#constrains").hide();
    // $("#period").hide();
    // $("#calibration").hide();
    // $("#config").hide();

    // constraint management
    $("#constraint-show").click((ev) => {
        let all_c_code = "";
        userdata = JSON.parse(localStorage.getItem("userdata"));
        if(userdata.constraints.length > 0){
            for(let i=0; i<userdata.constraints.length; i++){
                let item = userdata.constraints[i];
                let constraint_code = "<div class='form-inline'><div class='m-2'>\
                        <label for='c"+i+"max'>Constraint "+i+" upper limit</label><br/>\
                        <input type='number' id='c"+i+"max' name='c"+i+"max' value='"+item.maximum+"' step='any' required/>\
                    </div>\
                    <div class='m-2'>\
                        <label for='c"+i+"min'>Constraint "+i+" lower limit</label><br/>\
                        <input type='number' id='c"+i+"min' name='c"+i+"min' value='"+item.minimum+"' step='any' required/>\
                    </div></form>";
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
                userdata.constraints[i].minimum = min;
                userdata.constraints[i].maximum = max;
            }
            localStorage.setItem("userdata", JSON.stringify(userdata));
            $("#constrains").hide(400);
            // console.log(userdata);
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
                <input type='file' id='c"+i+"' name='c"+i+"' accept='.csv,.tif' required/>\
            </div>";
            all_c_code += constraint_code;
        }
        $("#constraint_fields").html(all_c_code);
    });

    $("#config-form").submit(async function(e){
        e.preventDefault();
        $("#loading").removeClass("d-none");
        configForm = document.querySelector("form");
        // handle submit;
        let formData = new FormData(configForm);
        try {
            const res = await fetch(
                '/process_form/',
                {
                    method: 'POST',
                    body: formData,
                },
            );
            let resData = await res.json().then(()=>{
                $("#loading").addClass("d-none");
                console.log("DONE");
            })
        } catch (err) {
            console.log(err.message);
        }
    });


    $("#download-form").submit(async function(e){
        e.preventDefault();
        let downloadForm = document.querySelector("#download-form");
        // handle submit;
        console.log(downloadForm);
        let formData = new FormData(downloadForm);
        try {
            const res = await fetch(
                '/download_data/',
                {
                    method: 'POST',
                    body: formData,
                },
            );
            let resData = await res.json();
            window.location.href
            window.open(resData.file, "_blank");
        } catch (err) {
            console.log(err.message);
        }
    });


    $("#play").click(() => {
        const update = () => {
            let index = 0;
            let num_call = 1;
            let req_id = 1
            index = parseInt($("#index").val());
            num_call = parseInt($("#num_call").val());
            req_id = parseInt($("#req_id").val());
            $.ajax({
                type: "POST",
                url: 'get_result/'+ index,
                data: {},
                dataType: "json",
                success: function (data) {
                    // any process in data
                    // console.log("****");
                    $("#num_call").attr("value", data.num_outputs);
                    $("#req_id").attr("value", data.req_id);
                    $("#index").attr("value", data.next);
                    $("#output_img").attr("src", "data:image/png;base64,"+data.file);
                    // console.log(data);
                },
                failure: function () {
                    console.log("failure");
                }
            });
        }
        let nIntervId = setInterval(update, 500);
        $("#btn-stop").click(()=>{
            clearInterval(nIntervId);
        })
    })

    $("#save_configs").click((ev) => {
        // userdata.project_folder = document.getElementById("pfolder").files[0].mozFullPath;
        userdata.shp_file = document.getElementById("shp_file").files[0].mozFullPath;
        userdata.dbf_file = document.getElementById("dbf_file").files[0].mozFullPath;
        userdata.shx_file = document.getElementById("shx_file").files[0].mozFullPath;
        let num_con = parseInt($("#num_cons").val());
        userdata.constraints = [];
        for(let i=0; i<num_con; i++){
            userdata.constraints.push({
                "file_path": document.getElementById("c"+i+"").files[0].mozFullPath,
                "minimum": 0,
                "maximum": 0,
            })
        }
        userdata.affected_area = document.getElementById("affected_area").files[0].mozFullPath;
        localStorage.setItem("userdata", JSON.stringify(userdata));
        console.log(userdata);
        $("#config").hide(400);
    });

    // $("#btn-run").click((ev) => {
    //     let userdata_ = JSON.parse(localStorage.getItem("userdata"));
    //     let data = {
    //         "data":userdata_
    //     }
    //     postData("/process/", data);
    //     $.ajax({
    //         type: "POST",
    //         url: '/process/',
    //         data: {
    //             "data": JSON.stringify(userdata_)
    //         },
    //         dataType: "json",
    //         success: function (data) {
    //             // any process in data
    //             alert("successfull")
    //         },
    //         failure: function () {
    //             alert("failure");
    //         }
    //     });
    // })

    // var map = L.map('map').setView([51.505, -0.09], 13);

    // L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //     attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    // }).addTo(map);

})