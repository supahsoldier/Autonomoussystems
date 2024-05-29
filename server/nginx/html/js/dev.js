
// obtain a list of all topics
const topicList = document.getElementById("mqttMessages");
let topics = [];
let dropdown = document.getElementById("mqttTopicSelect");

for (const element of topicList.children) {
    const topic = element.textContent.trim();
    topics.push(topic);
    
    const newElement = document.createElement("option");
    newElement.setAttribute("value", topic);
    newElement.innerText = topic;

    dropdown.appendChild(newElement);
}

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

    topics.forEach(topic => {
        mqttClient.subscribe(topic, { qos: 2 });
    });
});

mqttClient.on("connect", () => {
    console.log("Client connected: " + clientId);

    topics.forEach(topic => {
        mqttClient.subscribe(topic, { qos: 2 });
    });
});

// Received Message
mqttClient.on("message", (topic, message, packet) => {
    // Get all list items from the "mqttMessages" list
    const topicElements = document.getElementById("mqttMessages").querySelectorAll("li");

    // Find the matching list item based on the topic
    const matchingItem = [...topicElements].find(item => item.getAttribute("value") === topic);

    if (matchingItem) {
        // Update the inner HTML of the matching item with the message
        matchingItem.innerHTML = topic + ": <b>" + message + "</b>";
    } else {
        console.warn("Received message for unknown topic:", topic);
    }
});

function sendMain(){
    let msg = document.getElementById("mainInput");
    mqttClient.publish("application/front/in", msg.value, { qos: 2 });
    msg.value = "";
}

function sendGeneral(){
    let msg = document.getElementById("mqttMessageInput");
    const topic = document.getElementById("mqttTopicSelect");
    mqttClient.publish(topic.value, msg.value, { qos: 2 });
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
const mainButton = document.getElementById("mainSendBtn");
const generalButton = document.getElementById("mqttSendBtn");

mainButton.addEventListener("click", sendMain);
generalButton.addEventListener("click", sendGeneral);