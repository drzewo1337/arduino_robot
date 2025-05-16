#include <ESP8266WiFi.h>

// Konfiguracja sieci WiFi
// const char* ssid = "TP-LINK";
// const char* password = "12345678";

const char* ssid = "iPhoneXX";
const char* password = "minecraft";

// Port serwera TCP
WiFiServer server(23);  // Port 23 to standardowy port dla Telnet, ale można użyć dowolnego wolnego portu

void setup() {
  // Inicjalizacja portu szeregowego
  Serial.begin(115200);
  
  // Połączenie z siecią WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    //Serial.println("Łączenie z WiFi...");
  }
  //Serial.println("Połączono z WiFi!");
  Serial.print("Adres IP: ");
  Serial.println(WiFi.localIP());

  // Uruchomienie serwera
  server.begin();
  //Serial.println("Serwer TCP uruchomiony!");

  // Ustawienie LED_BUILTIN jako wyjście
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH); // Wyłączenie wbudowanej diody LED
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Nowy klient połączony");
    digitalWrite(LED_BUILTIN, LOW); // Włączenie wbudowanej diody LED
    while (client.connected()) {
      if (client.available()) {
        String command = client.readStringUntil('\n');
        command.trim(); // Usunięcie białych znaków na początku i końcu
        command += "\n";
        // Wysłanie komendy do Arduino
        Serial.print(command);
      }
    }
    client.stop();
    //Serial.println("Klient rozłączony");
  }
}




