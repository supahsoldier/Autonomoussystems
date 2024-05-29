//buttons 
let irLeft = document.querySelector('#irLeft');
let irRight = document.querySelector('#irRight');
let irFront = document.querySelector('#irFront');
let state = document.querySelector('#state');
let ultrasoon = document.querySelector('#ultrasoon');
let ultrasoonLeft = document.querySelector('#ultrasoonLeft');
let ultrasoonRight = document.querySelector('#ultrasoonRight');
let ldr = document.querySelector('#ldr');
let hall = document.querySelector('#hall');

//different messages for state change and motor movement
messageMG = new Paho.MQTT.Message("mg");
messageMG.destinationName = "chariot/move";
messageMG.qos = 2;

messageMB = new Paho.MQTT.Message("mb");
messageMB.destinationName = "chariot/move";
messageMB.qos = 2;

messageML = new Paho.MQTT.Message("ml");
messageML.destinationName = "chariot/move";
messageML.qos = 2;

messageMR = new Paho.MQTT.Message("mr");
messageMR.destinationName = "chariot/move";
messageMR.qos = 2;

messageMS = new Paho.MQTT.Message("ms");
messageMS.destinationName = "chariot/move";
messageMS.qos = 2;

//sensor states
var irLeftState;
var irRightState;
var irFrontState;
var state2;
var ultrasoonState;
var ultrasoonStateLeft;
var ultrasoonStateRight;
var ldrState;
var hallState;

var clientId = "clientId-" + makeClientId(10);

// Create a client instance
client = new Paho.MQTT.Client("127.0.0.1", Number(1884), clientId);

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});

// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription

  var subscribeOptions = {
	qos: 2,  // QoS
  };

  console.log("Connected");
  client.subscribe("ACM/29/client/irLeft", subscribeOptions);
  client.subscribe("ACM/29/client/irRight", subscribeOptions);
  client.subscribe("ACM/29/client/irFront", subscribeOptions);
  client.subscribe("ACM/29/client/ultrasoon", subscribeOptions);
  client.subscribe("ACM/29/client/ultrasoonLeft", subscribeOptions);
  client.subscribe("ACM/29/client/ultrasoonRight", subscribeOptions);
  client.subscribe("ACM/29/client/ldr", subscribeOptions);
  client.subscribe("ACM/29/client/hall", subscribeOptions);
  client.subscribe("ACM/29/client/state", subscribeOptions);
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
  clientId = "clientId-" + makeClientId(10);
  client = new Paho.MQTT.Client("broker.mqttdashboard.com", Number(8000), clientId);
  client.connect({onSuccess:onConnect});
}

// called when a message arrives
function onMessageArrived(message) {
    switch(message.destinationName){
        case "ACM/29/client/state":
            state2 = message.payloadString;
            break;
        case "ACM/29/client/irLeft":
            irLeftState = message.payloadString;
            break;
        case "ACM/29/client/irRight":
            irRightState = message.payloadString;
            break;
        case "ACM/29/client/irFront":
            irFrontState = message.payloadString;
            break;
        case "ACM/29/client/ultrasoon":
            ultrasoonState = message.payloadString;
            break;
        case "ACM/29/client/ultrasoonLeft":
            ultrasoonStateLeft = message.payloadString;
            break;
        case "ACM/29/client/ultrasoonRight":
            ultrasoonStateRight = message.payloadString;
            break;
        case "ACM/29/client/ldr":
            ldrState = message.payloadString;
            break;
        case "ACM/29/client/hall":
            hallState = message.payloadString;
            break;
    }
    updateScreen();
}

function go() {
    client.send(messageMG);
}

function back() {
    client.send(messageMB);
}

function right() {
    client.send(messageMR);
}

function left() {
    client.send(messageML);
}

function stop() {
    client.send(messageMS);
}

function updateScreen(){
    if(irLeftState == "0"){
        irLeft.innerHTML = "InfraRed Left: FALSE";
        irLeft.classList.remove("active");
    }
    else{
        irLeft.innerHTML = "InfraRed Left: TRUE";
        irLeft.classList.add("active");
    }

    if(irRightState == "0"){
        irRight.innerHTML = "InfraRed Right: FALSE";
        irRight.classList.remove("active");
    }
    else{
        irRight.innerHTML = "InfraRed Right: TRUE";
        irRight.classList.add("active");
    }

    if(irFrontState == "0"){
        irFront.innerHTML = "InfraRed Front: FALSE";
        irFront.classList.remove("active");
    }
    else{
        irFront.innerHTML = "InfraRed Front: TRUE";
        irFront.classList.add("active");
    }

    if(ldrState == "0"){
        ldr.innerHTML = "LDR: FALSE";
        ldr.classList.remove("active");
    }
    else{
        ldr.innerHTML = "LDR: TRUE";
        ldr.classList.add("active");
    }

    if(hallState == "0"){
        hall.innerHTML = "Hall Effect: FALSE";
        hall.classList.remove("active");
    }
    else{
        hall.innerHTML = "Hall Effect: TRUE";
        hall.classList.add("active");
    }

    ultrasoon.innerHTML = "Ultrasoon: " + ultrasoonState;
    ultrasoonLeft.innerHTML = "Ultrasoon Left: " + ultrasoonStateLeft;
    ultrasoonRight.innerHTML = "Ultrasoon Right: " + ultrasoonStateRight;

    switch(state2){
        case "0":
            state.innerHTML = "Current State: IDLE";
            break;
        case "1":
            state.innerHTML = "Current State: AUTOPILOT";
            break;
        case "2":
            state.innerHTML = "Current State: OBJECT AVOIDANCE";
            break;
        case "3":
            state.innerHTML = "Current State: TUNNEL";
            break;
    }
}

function makeClientId(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}