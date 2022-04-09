    // CAMERA SETTINGS.
    Webcam.set({
        width: 480,
        height: 480,
        image_format: 'jpeg',
        jpeg_quality: 100,
		flip_horiz: true

    });
    Webcam.attach('#camera');

    // TAKE A SNAPSHOT.
    takeSnapShot = function () {
        Webcam.snap(function (data_uri) {
            downloadImage('yourface', data_uri);
        });
    }

    // DOWNLOAD THE IMAGE.
    downloadImage = function (name, datauri) {
        var a = document.createElement('a');
        a.setAttribute('download', name + '.png');
        a.setAttribute('href', datauri);
        a.click();
    }