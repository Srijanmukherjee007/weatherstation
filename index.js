const http = require("http");

const httpHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "text/html"
};

const server = http.createServer((_, res) => {
    res.writeHead(200, httpHeaders);
    res.write("ok");
    res.end();
});

const { Server } = require("socket.io");
const io = new Server(server);


let IOT_ACTIVE = false;
const IOT_KEY = "*2138192AHKHSBANM%^#@!@#^%&$%"; // TODO store in env

const CLIENT_ROOM = "client";
const IOT_ROOM = "iot";
const DATA_PROTOCOL = {
    temperature: Number,
    humidity: Number
};

function respondError(message) {
    return {
        error: message
    };
}

function respondSuccess(message) {
    return {
        success: message
    };
}

io.on("connection", (socket) => {
    socket.join(CLIENT_ROOM);

    // register weather station
    socket.on("upgrade", (req) => {
        const upgradeKey = req["UPGRADE-KEY"];

        if (!upgradeKey || upgradeKey !== IOT_KEY) {
            return socket.send(respondError("upgrade failed"));
        }

        socket.leave(CLIENT_ROOM);
        socket.join(IOT_ROOM);
        socket.send(respondSuccess("upgraded"));
    });

    socket.on("update", (req) => {
        console.log(socket.rooms);
    })
})


server.listen(8080);