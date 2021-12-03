#include "DHT.h"
#define DHTPIN 2     
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  
  delay(2000);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (!isnan(temperature) && !isnan(humidity)) {
    Serial.print("{\"temperature\":");
    Serial.print(temperature);
    Serial.print(", \"humidity\":");
    Serial.print(humidity);
    Serial.print("}\n");
  }
}
