// Calls the API /search?q="""
function submitSearch(e) {

    var apigClient = apigClientFactory.newClient();

    var params = {
        'q': document.getElementById("input-search").value,
    };

    apigClient.searchGet(params, {}, {})
        .then(function (result) {
            displayImage(result);
        }).catch(function (result) {
            console.log(result);
        });
}

// voice search
function submitVoice(file) {

    var file_name = "Recording.wav";

    var apigClient = apigClientFactory.newClient();

    var additionalParams = {
        headers: {
            'Content-Type': file.type,
        }
    }

    url = "https://lenhfz78se.execute-api.us-east-1.amazonaws.com/v1/upload/s3-voice-recording-photo-album/" + file_name
    axios.put(url, file, additionalParams).then(response => {

        var params = {
            'q': 'searchAudio',
        };

        apigClient.searchGet(params, {}, {}).then(function (result) {
            displayImage(result);
        }).catch(function (result) {
            console.log('wait... still searching')
        });
        console.log("Voice uploaded: " + file_name);
    });

}

function displayImage(result) {
    console.log("result", result);

    img_paths = result["data"]
    var div = document.getElementById("imgDiv");
    div.innerHTML = '<h2>Photo Grid</h2>';

    var j;
    for (j = 0; j < img_paths.length; j++) {
        img_ls = img_paths[j].split('/');
        img_name = img_ls[img_ls.length - 1];
        div.innerHTML += '<div class="col-md-3 mx-auto"><div class="card text-dark"><img src="' + img_paths[j] + '" class="card-img-top"><div class="card-body">' +
            '<p class="card-text">' + img_name + '</p></div ></div ></div >';
    }
}


function submitPhoto(e) {

    if (!window.File || !window.FileReader || !window.FileList || !window.Blob) {
        alert('The File APIs are not fully supported in this browser.');
        return;
    }

    var path = (document.getElementById("input-file").value).split("\\");
    customLabels = document.getElementById("input-customLabels").value;
    var file_name = path[path.length - 1];

    console.log(file_name);

    var file = document.getElementById("input-file").files[0];
    console.log(file);

    // const reader = new FileReader();

    // var apigClient = apigClientFactory.newClient();

    if (customLabels.length != 0) {
        var additionalParams = {
            headers: {
                'Content-Type': file.type,
                'x-amz-meta-customlabels': customLabels
            }
        };
    } else {
        var additionalParams = {
            headers: {
                'Content-Type': file.type,
            }
        };
    }


    console.log(additionalParams)

    console.log(file.name.split('.')[0])

    url = "https://lenhfz78se.execute-api.us-east-1.amazonaws.com/v1/upload/photoalbumcloudassignment3/" + file.name
    axios.put(url, file, additionalParams).then(response => {
        console.log(response)
        alert("Image uploaded: " + file.name);
    }).catch(function (result) {
        console.log("result", result);
    });

}