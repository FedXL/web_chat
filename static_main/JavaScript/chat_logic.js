
const socketEndpoint = document.getElementById('socket').textContent; // Переменная, переданная из Python
const ws = new WebSocket(socketEndpoint); // Используйте socketEndpoint для создания WebSocket
console.log(socketEndpoint);



const EventToSend = {
    message: 'message',
    newToken: 'newToken',
    askUsername: 'askUsername',
    downloadHistory: 'downloadHistory'
};

const MessageTypeToSend = {
    text: 'text',
    photo: 'photo',
    document: 'document'
};

let MessageLoadToSendExample = {
    event: EventToSend.message,
    name: null,
    details: {
        message_id: null,
        is_answer: false,
        user_id: null,
        message_type: MessageTypeToSend.text,
        text: null
    }
};


document.getElementById('uploadButton').addEventListener('click', function () {
    document.getElementById('imageInput').click();
});


document.getElementById('imageInput').addEventListener('change', function () {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (file) {

        let fileType;
        let messageType;

        const fileName = file.name.toLowerCase();
        const reader = new FileReader();


        if (fileName.endsWith('.pdf')) {
            messageType = 'document';
            fileType = '.pdf';
            console.log('Uploaded file is a PDF.');
            console.log(fileType);

        } else if (fileName.match(/\.(jpg|jpeg|png|gif|bmp)$/)) {
            messageType = 'photo';
            fileType = fileName.match(/\.(jpg|jpeg|png|gif|bmp)$/)[0];
            console.log('Uploaded file is an image.');
            console.log(fileType);
        } else {console.log('Uploaded file is of an unknown type.'); }

        reader.onload = (event) => {
            const fileBase64 = btoa(event.target.result);

            let jsonData = MessageLoadToSendExample;
            jsonData.details.text = fileBase64;
            jsonData.details.message_type = messageType;
            jsonData.details.extension = fileType;


            ws.send(JSON.stringify(jsonData));
            console.log("File sent via WebSocket.");
            console.log(jsonData)
        }
        reader.readAsBinaryString(file);
    }
});


document.getElementById("join-btn").addEventListener("click",function(){
    let username = document.getElementById("username").value;
    document.getElementById("chat").style.display = "block";
    document.getElementById("landing").style.display = "none";
    document.getElementById('messages').style.display ="block"
    sendUsername(username);
    let expirationDate = new Date();
    expirationDate.setMonth(expirationDate.getMonth() + 2);
    let expires = expirationDate.toUTCString();
    document.cookie = "name=" + username + "; expires=" + expires + "; path=/";
});


ws.onopen = function() {
    console.log('Соединение установлено');
    sendChecker();
};

ws.onmessage = function(event) {
    let messagesDiv = document.getElementById('messages');
    console.log('получено сообщение OnMessage');
    let messageData = JSON.parse(event.data);

    if (messageData.event === 'ask_username') {
        console.log('start ask username event')
        document.getElementById('chat').style.display = 'none';
        document.getElementById('landing').style.display = 'block';

    } else if (messageData.event === 'message') {
        document.getElementById('messages').style.display ="block"
        console.log('start message event');
        if (messageData.details.message_type === 'text') {
            addMessageEventText(messagesDiv,messageData);

        } else if (messageData.details.message_type === 'photo'){
            console.log('photo branch');
            addPhoto(messageData.details, messagesDiv);
        } else if (messageData.details.message_type === 'document'){
            console.log('document branch');
            console.log(messageData.details);
        }

        scrollDown();

    } else if (messageData.event === 'new_token') {
        console.log('new token recieved')
        let loadData = messageData.data;
        let expirationDate = new Date();
        expirationDate.setMonth(expirationDate.getMonth() + 2);
        let expires = expirationDate.toUTCString();
        document.cookie = "token=" + loadData + "; expires=" + expires + "; path=/";

    } else if (messageData.event === 'download_history'){
        console.log('download history event : history recievied');
        document.getElementById('chat').style.display ="block";
        console.log(messageData);
        let myArray = messageData.data;
        console.log(myArray.length)

        for (let i = 0; i < myArray.length; i++) {
            console.log(myArray[i]);
            if (myArray[i].message_type === 'photo'){
                addPhoto(myArray[i], messagesDiv);
            } else if (myArray[i].message_type === 'text'){
                addTextStringFromHistory(messagesDiv,myArray[i]);
            } else if (meArray[i].message_type === 'document'){
                console.log('it child to be a photo!');
            }
        }

        scrollDown();
    }
};


ws.onclose = function(event) {
    console.log('Соединение закрыто');
};


function addMessageEventText(mdiv,data){
    console.log('start add message event');
    console.log(data);
    let nameValue = data.name;
    if (data.details.is_answer === true){
        let text = nameValue+": " + data.details.text;
        let messageElement = createAnswerTextElement(text);
        mdiv.appendChild(messageElement);
    } else if (data.details.is_answer === false){
        let text = nameValue+": " + data.details.text;
        let messageElement = createQuestionTextElement(text);
        mdiv.appendChild(messageElement);
    }
}
function scrollDown() {
    const scrollableDiv = document.getElementById("messages");
    setTimeout(function () {
        scrollableDiv.scrollTop = scrollableDiv.scrollHeight;
    }, 1000); // Задержка в одну секунду (1000 миллисекунд)
}
function addTextStringFromHistory(mdiv, data) {
    console.log('start add text');
    console.log(data);
    let name = data.user_name;
    if (data.is_answer === false) {
        let text = name + ": "+ data.text;
        let messageElemnt = createQuestionTextElement(text);
        mdiv.appendChild(messageElemnt);
    } else if (data.is_answer === true) {
        let text = data.text;
        let messageElement = createAnswerTextElement(text);
        mdiv.appendChild(messageElement);
    } else {
        console.log("Unexpected value for is_answer:", data.is_answer);
    }
}



function sendMessage() {
    let messageInput = document.getElementById('messageInput');
    let message = messageInput.value;
    let data = MessageLoadToSendExample;
    data.details.text = message;
    data.details.message_type= MessageTypeToSend.text;
    console.log(data);
    ws.send(JSON.stringify(data));
    messageInput.value = '';
}


function sendUsername(UserName) {
    let data = {
        event: "username",
        username: UserName
    };
    ws.send(JSON.stringify(data));
}


function sendChecker(){
    let data = {
        event: "onconnect"};
    ws.send(JSON.stringify(data));
}


function createQuestionTextElement(messageText) {
    let messageContainer = document.createElement('div');
    messageContainer.classList.add('messageContainer');
    let messageQuestion = document.createElement('div');
    messageQuestion.classList.add('messageQuestion');
    messageQuestion.textContent = messageText;
    let spacer = document.createElement('div');
    spacer.classList.add('spacer');
    messageContainer.appendChild(messageQuestion);
    messageContainer.appendChild(spacer);
    return messageContainer;
}


function createAnswerTextElement(messageText){
    let messageContainer = document.createElement('div');
    messageContainer.classList.add('messageContainer');
    let messageAnswer = document.createElement('div');
    messageAnswer.classList.add('messageAnswer');
    messageAnswer.textContent = messageText;
    let spacer = document.createElement('div');
    spacer.classList.add('spacer');
    messageContainer.appendChild(spacer);
    messageContainer.appendChild(messageAnswer);
    return messageContainer;
}

function addFullscreenHandler(image) {
    image.addEventListener("click", function () {
        if (!image.classList.contains("fullscreen")) {
            image.style.maxWidth = "100%"; // Убираем максимальную ширину
            image.style.maxHeight = "100%"; // Убираем максимальную высоту
            image.classList.add("fullscreen");
        } else {
            image.style.maxWidth = "100px"; // Возвращаем максимальную ширину 300px
            image.style.maxHeight = "100px"; // Возвращаем максимальную высоту 300px
            image.classList.remove("fullscreen");
        }
    });
}

function addPhoto(data, mdiv) {
    console.log('start add photo');
    console.log(data);

    let text;
    if (data.body) {
        text = data.body;
    } else if (data.text) {
        text = data.text;
    }
    console.log(text);
    let is_answer = data.is_answer;
    let imageElement = document.createElement('img');
    imageElement.classList.add("image");
    addFullscreenHandler(imageElement);
    imageElement.src = text
    imageElement.style.maxWidth='100px';
    imageElement.style.maxHeight='100px';
    let messageContainer= document.createElement('div');
    messageContainer.classList.add('messageContainer');
    if (is_answer === true) {
        let messageAnswer = document.createElement('div');
        messageAnswer.classList.add('messageAnswer');
        messageAnswer.appendChild(imageElement);
        let spacer = document.createElement('div');
        spacer.classList.add('spacer');
        messageContainer.appendChild(spacer);
        messageContainer.appendChild(messageAnswer);
    } else if (is_answer === false) {
        let messageQestion = document.createElement('div');
        messageQestion.classList.add('messageQuestion');
        messageQestion.appendChild(imageElement);
        let spacer = document.createElement('div');
        spacer.classList.add('spacer');
        messageContainer.appendChild(messageQestion);
        messageContainer.appendChild(spacer);
    }
    mdiv.appendChild(messageContainer);
    return messageContainer
}
