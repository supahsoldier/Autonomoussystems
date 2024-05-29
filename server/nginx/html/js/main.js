// connect to mqtt
let mqttClient;
const clientId = makeClientId(10);
const host = "ws://" + location.host + ":1884/";

const options = {
// username: uname,
// password: pass,
clientId: clientId,
clean: true,
connectTimeout: 30 * 1000,
};

mqttClient = mqtt.connect(host, options);

mqttClient.on("error", (err) => {
    console.log("Error: ", err);
    mqttClient.end();
});

mqttClient.on("reconnect", () => {
    console.log("Reconnecting...");
});

mqttClient.on("connect", () => {
    console.log("Client connected: " + clientId);
});

function sendMain(){
    let msg = document.getElementById("mainInput");
    mqttClient.publish("application/front/in", msg.value, { qos: 2 });
    msg.value = "";
}

//returns a random client id given a certain length
function makeClientId(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

//set event listeners
const mainButton = document.getElementById("mainSend");
mainButton.addEventListener("click", sendMain);