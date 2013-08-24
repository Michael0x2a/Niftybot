var url = "http://" + document.domain + ":5000";

function isPrimitive(obj) {
    var isBool = (typeof obj === "boolean" || obj instanceof Boolean);
    var isNum = (typeof obj === "number" || obj instanceof Number);
    var isString = (typeof obj === "string" || obj instanceof String);
    var isNull = (obj === null);
    
    return isBool || isNum || isString || isNull;
}

function parseSingle(name, data)
{
    if (data === "(HIDDEN)")
    {
        return "";
    } else {
        return "<li>" + name + ": " + data + "</li>";
    }
}

function parseJSON(data)
{
    var output = "<ul>";
    $.each(data, function(item, element) {
        if (isPrimitive(element)) {
            output += parseSingle(item, element);
        } else {
            var temp = "<li>" + item + parseJSON(element) + "</li>";
            output += temp;
        }
    });
    return output + "</ul>";
}

function display(htmlId, data, name) {
    if (data.success) {
        $(htmlId).html(parseJSON(data[name]));
    } else {
        $(htmlId).html(data.reason);
    }
}

function updateRobot() {
    var callback = function() {
        $.getJSON(url + "/state/robot")
            .done(function(data) {
                display("#robot-state", data, "robot");
            });
    };

    window.setInterval(callback, 500);
}
    
function updateState() {
    var callback = function() {
        $.getJSON(url + "/state/state")
            .done(function(data) {
                var newData = {
                    "success": data.success, 
                    "state": data.state.state, 
                };
                display("#decision-state", newData, "state");
            });
    }
    window.setInterval(callback, 500);
}


function getPosition(e) {
    var target;

    if (!e) {
        e = window.event;
    }
    
    if (e.target)
    {
        target = e.target;
    } else if (e.srcElement) {
        target = e.srcElement;
    }
    
    if (target.nodeType == 3) { // Fixes Safari bug
        target = target.parentNode;
    }

    var x = e.pageX - $(target).offset().left;
    var y = e.pageY - $(target).offset().top;
    
    return {"x": x, "y": y};
};

function updateData(data) {
    $.ajax({
        url: url + "/state/straight",
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({"data": data}),
        dataType: 'json',
        async: true
    });
}

function calculateRelativePosition(canvasObj, pos) {
    return {
        "x": pos.x / canvasObj.width * 2 - 1,
        "y": pos.y / canvasObj.height * -2 + 1,
        "original": pos
    };
}

function drawManual(canvasObj, position) {
    canvasObj.context.setTransform(1, 0, 0, 1, 0, 0);
    canvasObj.context.clearRect(
        0,
        0,
        canvasObj.width,
        canvasObj.height);
    canvasObj.context.restore();
    canvasObj.context.beginPath();
    canvasObj.context.arc(
        position.original.x, 
        position.original.y, 
        10,         // radius
        0,          // start angle
        Math.PI * 2,
        true);
    canvasObj.context.fill();
}

function setupControls() {
    var htmlId = "wheels";

    var canvas = document.getElementById(htmlId);
    var canvasObj = {
        "canvas": canvas,
        "context": canvas.getContext('2d'),
        "height": canvas.height,
        "width": canvas.width,
        "centerx": canvas.width/2,
        "centery": canvas.width/2
    };
    
    var isClicked = false;
    var position = {"x": 0, "y": 0, "original": {
        "x": canvasObj.centerx, 
        "y": canvasObj.centery
    }};

    var handlePress = function(event) {
        if (!isClicked) {
            return;
        }

        position = calculateRelativePosition(
            canvasObj,
            getPosition(event));
    }
    
    $('#' + htmlId).mousedown(function() { isClicked = true; });
    $(document).mouseup(function() { 
        isClicked = false; 
        
        position = {"x": 0, "y": 0, "original": {
            "x": canvasObj.centerx, 
            "y": canvasObj.centery
        }};

        updateData([
            ["straight", position.y],
            ["rotate", position.x]
        ]);
        drawManual(canvasObj, position);
    });

    $("#" + htmlId).mousemove(handlePress);

    window.setInterval(function() {
        if (position.x == 0 && position.y == 0) {
            return;
        }

        drawManual(canvasObj, position);
        updateData([
            ["straight", position.y],
            ["rotate", position.x]
        ]);
    }, 100);
}

var isManualEnabled = false;

function toggleManual(htmlId) {
    $(htmlId).click(function(event){
        if (isManualEnabled) {
            $(htmlId).html("Turn manual on?");
            $(htmlId).addClass('off').removeClass('on');
            updateData([['manual', false]]);
        } else {
            $(htmlId).html("Turn manual off?");
            $(htmlId).addClass('on').removeClass('off');
            updateData([['manual', true]]);
        }
        isManualEnabled = !isManualEnabled;
    });
}

function updateVideo(htmlId) {
    if ("WebSocket" in window) {
        var cam = new WebSocket("ws://" + document.domain + ":5000/camera");
        cam.onmessage = function (msg) {
            $(htmlId).attr('src', 'data:image/jpg;base64,' + msg.data);
        };
        cam.onerror = function(e) {
            console.log(e);
        }
    } else {
        alert("Warning: Your browser does not support websockets. You cannot view the camera feed.");
    }
}
