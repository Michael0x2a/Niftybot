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

function updateRobot(name, value) {
    $.ajax({
        url: url + "/state/straight",
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({"value": value, "name": name}),
        dataType: 'json',
        success: function(response) {
        }
    });
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
    
    $("#" + htmlId).click(function(event) {
        position = getPosition(event);
        updateRobot("manual", true);
        updateRobot("straight", 1.0);
    });
}

var isManualEnabled = false;

function toggleManual(htmlId) {
    $(htmlId).click(function(event){
        if (isManualEnabled) {
            $(htmlId).html("Turn manual on?");
            updateRobot('manual', false);
        } else {
            $(htmlId).html("Turn manual off?");
            updateRobot('manual', true);
        }
        isManualEnabled = !isManualEnabled;
    });
}

