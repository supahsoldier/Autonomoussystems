function setFeed() {
    // Get references to elements
    const ipElement = document.getElementById("cameraIP");
    const portElement = document.getElementById("cameraPort");
    const okButton = document.getElementById("cameraConnectBtn");
    const feedTitle = document.getElementById("feedTitle");
    
    const ip = ipElement.value;
    const port = portElement.value;

    const feed = "http://" + ip + ":" + port + "/video";

    // Remove elements
    ipElement.parentNode.removeChild(ipElement);
    portElement.parentNode.removeChild(portElement);
    okButton.parentNode.removeChild(okButton);
    feedTitle.parentNode.removeChild(feedTitle);
  
    // Create the new element
    const newElement = document.createElement("img");
    newElement.classList.add("feed");
    newElement.setAttribute("width", "616");
    newElement.setAttribute("height", "347");
    newElement.setAttribute("src", feed);
  
    // Get the parent element where the caemra feed will be added
    const parentElement = document.getElementById("cameraFeed");
  
    // Add the new element to the parent
    parentElement.appendChild(newElement);
  }

const feedButton = document.getElementById("cameraConnectBtn");
feedButton.addEventListener("click", setFeed);
