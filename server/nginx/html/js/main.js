
//connect to mqtt server
let mqttClient;
let userLST = [];

const clientId = makeClientId(10);
const host = "ws://127.0.0.1:1884/";

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
    mqttClient.subscribe("chat/message", { qos: 2 });
    userLST.push("user-" + clientId);
    addUser("YOU: user-" + clientId);
    mqttClient.publish("chat/message", "user-" + clientId + " joined the chat", { qos: 2 });
});

// Received Message
mqttClient.on("message", (topic, message, packet) => {

    if(topic.includes("chat/message")){
        addMessage(message, getDate());
        if(message.includes("joined the chat")){
            username = message.toString().split(" ")[0];

            if(!userLST.includes(username)){
                userLST.push(username);
                addUser(username);
            }

        }
        
    }
});

let inputMSG = document.getElementById("msg")
inputMSG.addEventListener("keydown", function(event) {
    // Check if the "Enter" key was pressed (keyCode 13)
    if (event.key === "Enter") {
        sendMessage();
    }
});

//function for sending message and clearing input field
function sendMessage(){
    mqttClient.publish("chat/message", inputMSG.value, { qos: 2 });
    inputMSG.value = "";
}

//adds user to the user list on the screen
function addUser(username){
    let users = document.getElementById("participants");

    let text = document.createElement("h6");
    text.classList.add("mb-0");
    text.textContent = username;

    let newUser = document.createElement("div");
    newUser.classList.add("card");
    newUser.classList.add("user");
    newUser.classList.add("d-flex");

    newUser.appendChild(text);
    users.appendChild(newUser);
}

//displays a message on the screen
function addMessage(message, date){
    let messages = document.getElementById("messages");
    
    let message_p = document.createElement("p");
    let date_p = document.createElement("p");

    let div_third = document.createElement("div");
    let div_second = document.createElement("div");
    let div_first = document.createElement("div");

    div_first.classList.add("media");
    div_first.classList.add("w-100");
    div_first.classList.add("mb-3");

    div_second.classList.add("media-body");
    div_second.classList.add("ml-3");

    div_third.classList.add("bg-primary");
    div_third.classList.add("rounded");
    div_third.classList.add("py-2");
    div_third.classList.add("px-3");
    div_third.classList.add("mb-2");

    message_p.classList.add("text-small");
    message_p.classList.add("mb-0");
    message_p.classList.add("text-white");
    message_p.textContent = message;

    date_p.classList.add("small");
    date_p.classList.add("text-muted");
    date_p.textContent = date;

    div_first.appendChild(div_second);
    div_second.appendChild(div_third);
    div_second.appendChild(date_p);
    div_third.appendChild(message_p);

    messages.appendChild(div_first);
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

//returns the date as string
function getDate(){
    const currentDate = new Date();

    let hours = currentDate.getHours();
    let minutes = currentDate.getMinutes();

    // Convert hours to AM/PM format
    const amPm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    const month = monthNames[currentDate.getMonth()];

    // Format the date and time
    const formattedDateTime = `${hours}:${minutes} ${amPm} | ${month} ${currentDate.getDate()}`;

    return formattedDateTime
}

