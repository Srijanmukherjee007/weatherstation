"use strict";

((global) => {
    document.addEventListener("DOMContentLoaded", main);
    const server = "http://localhost:8080";

    function main() {
        const socket = io(server);

        let disconnectTimeout = null;
        let weatherStationTimeout = null;

        socket.on("connect", () => {
            clearTimeout(disconnectTimeout);
            information.classList.add("hidden");
            server_status.classList.remove("hidden");
            server_status.innerText = "server connected";
            loader.classList.add("hidden");
        });

        // weather information
        socket.on("update", (data) => {
            if (information.classList.contains("hidden")) {
                information.classList.remove("hidden");
                server_status.classList.add("hidden");
            }

            document.querySelector(".temperature .value").innerText = data["temperature"];
            document.querySelector(".humidity .value").innerText = data["humidity"];
            document.querySelector(".location").innerText = data["location"];
            document.querySelector(".last_update").innerText = `Last update: ${data["timestamp"]}`;
        });

        socket.on("weather-station-disconnected", () => {
            clearTimeout(weatherStationTimeout);
            document.querySelector(".pop_up_message").innerText = "Weather station disconnected";
            document.querySelector(".pop_up_message").classList.remove("hidden");
        });

        socket.on("weather-station-connected", () => {
            document.querySelector(".pop_up_message").innerText = "Weather station connected";
            document.querySelector(".pop_up_message").classList.remove("hidden");

            weatherStationTimeout = setTimeout(() => {
                document.querySelector(".pop_up_message").classList.add("hidden");
            }, 2000);
        });

        socket.on("weather-station-status", (status) => {
            if (status) {
                document.querySelector(".pop_up_message").innerText = "Weather station connected";
                document.querySelector(".pop_up_message").classList.remove("hidden");

                weatherStationTimeout = setTimeout(() => {
                    document.querySelector(".pop_up_message").classList.add("hidden");
                }, 2000);
            } else {
                clearTimeout(weatherStationTimeout);
                document.querySelector(".pop_up_message").innerText = "Weather station disconnected";
                document.querySelector(".pop_up_message").classList.remove("hidden");
            }
        })

        socket.on("disconnect", () => {
            information.classList.add("hidden");
            server_status.classList.remove("hidden");
            server_status.innerText = "server disconnected";

            disconnectTimeout = setTimeout(() => {
                server_status.classList.add("hidden");
                loader.classList.remove("hidden");
            }, 2000);
        });


    }
})(window);