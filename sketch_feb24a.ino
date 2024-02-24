#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>



const int trigPin = D2;  // GPIO pin connected to the HC-SR04 sensor's TRIG pin
const int echoPin = D1;  // GPIO pin connected to the HC-SR04 sensor's ECHO pin

const char* ssid = "NodeMCU_AP";
const char* password = "12345678"; // Password must be 8+ characters for WPA2

ESP8266WebServer server(80); // Server will run on port 80


void setup() {
  Serial.begin(9600);  // Starts the serial communication
  WiFi.softAP(ssid, password); // Sets up the NodeMCU as an Access Point
  IPAddress myIP = WiFi.softAPIP(); // Gets the IP address of the NodeMCU AP
  Serial.print("AP IP address: ");
  Serial.println(myIP); 
  
  server.on("/", [](){ // Lambda function to handle root URL requests
    server.send(200, "text/html", "<h1>Welcome to NodeMCU Web Server!</h1>");
  });

  server.begin(); // Starts the web server
  Serial.println("Web server started");

  pinMode(trigPin, OUTPUT);  // Sets the trigPin as an Output
  pinMode(echoPin, INPUT);  // Sets the echoPin as an Input




}

void loop() {

  server.handleClient(); // Handles incoming client requests

  /*
  long duration, distance;
  digitalWrite(trigPin, LOW);  // Clears the trigPin condition
  delayMicroseconds(2);  // Waits for 2 microsecond
  digitalWrite(trigPin, HIGH);  // Sets the trigPin HIGH (ACTIVE) for 10 microseconds
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);  // Reads the echoPin, returns the sound wave travel time in microseconds
  distance= duration*0.034/2;  // Calculating the distance
  Serial.print("Distance: ");  // Prints the distance on the Serial Monitor
  Serial.println(distance);
  
  delay(2000);  // Wait for 2 seconds before the next loop for the next distance measurement
  */


}
