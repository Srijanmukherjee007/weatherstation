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
const io = new Server(server, {
    cors: {
        origin: "*"
    }
});


let IOT_ACTIVE = false;
const IOT_KEY  = "*2138192AHKHSBANM%^#@!@#^%&$%"; // TODO store in env

const CLIENT_ROOM = "client";
const IOT_ROOM    = "iot";
const DATA_PROTOCOL = Object.freeze({
    temperature: Number,
    humidity: Number
});

let prevData = Object.keys(DATA_PROTOCOL).reduce((obj, key) => {
    obj[key] = null
    return obj;
}, {});

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

function validateData(protocol, data) {
    if (!data) return { validatedError: null, error: "invalid request" };

    let errors = [];
    const validatedData = {};

    for (const key in protocol) {
        if (!data[key]) errors.push(`'${key}' not provided`);
        else if (protocol[key](data[key]) != data[key]) errors.push(`'${key}' has invalid datatype`);
        else validatedData[key] = protocol[key](data[key]);
    }

    return {
        validatedData,
        error: errors.length == 0 ? null : errors,
    };
}

function timestamp() {
    const date = new Date();
    return `${date.toLocaleTimeString()} ${date.toLocaleDateString()}`;
}

io.on("connection", (socket) => {
    socket.join(CLIENT_ROOM);
    socket.isIOT = false;
    socket.iotLocation = null;

    socket.emit("update", prevData);
    socket.emit("weather-station-status", IOT_ACTIVE);

    // register weather station
    socket.on("upgrade", (req) => {
        const upgradeKey = req["UPGRADE-KEY"];
        const location = req["location"];

        if (!upgradeKey || upgradeKey !== IOT_KEY || !location) {
            return socket.emit("upgrade-error", respondError("upgrade failed"));
        }

        socket.leave(CLIENT_ROOM);
        socket.join(IOT_ROOM);
        socket.isIOT = true;
        socket.iotLocation = location;
        socket.emit("upgrade-success", respondSuccess("upgraded"));
        
        IOT_ACTIVE = true;

        io.to(CLIENT_ROOM).emit("weather-station-connected");
        console.log(`[${timestamp()}] IOT UPGRADE weather station connected`);
    });

    // receive weather station update
    socket.on("update", (req) => {
        if (!socket.isIOT) {
            return socket.emit("update-error", respondError("you don't have authority to publish data"));
        }

        const { validatedData, error } = validateData(DATA_PROTOCOL, req);

        if (error) {
            return socket.emit("update-error", respondError(error));
        }

        validatedData["timestamp"] = new Date().toUTCString();
        validatedData["location"] = socket.iotLocation;
        prevData = validatedData;

        console.log(validatedData);

        io.to(CLIENT_ROOM).emit("update", validatedData);
    });

    socket.on("disconnect", () => {
        if (socket.isIOT) {
            IOT_ACTIVE = false;
            console.log(`[${timestamp()}] IOT weather station disconnected`);
            io.to(CLIENT_ROOM).emit("weather-station-disconnected");
        }
    })
});

server.listen(8080, () => {
    console.log(`[${timestamp()}] Listening on :8080`);
});