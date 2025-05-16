// Piny do sterowania silnikami

const int RPWM_Output1 = 5; // Prawy silnik, obrót w tył
const int LPWM_Output1 = 6; // Prawy silnik, obrót w przód
const int RPWM_Output2 = 10; // Lewy silnik, obrót w tył
const int LPWM_Output2 = 11; // Lewy silnik, obrót w przód

const int Speed_pin = 9; // Pin do sterowania prędkością silników

int speed = 255; // Szybkość silników, wartość PWM (0-255)
int speed2 = 120;

void setup() {
  // Inicjalizacja pinów silników
  pinMode(RPWM_Output1, OUTPUT);
  pinMode(LPWM_Output1, OUTPUT);
  pinMode(RPWM_Output2, OUTPUT);
  pinMode(LPWM_Output2, OUTPUT);

  Serial.begin(9600); // Inicjalizacja komunikacji szeregowej dla debugowania
  Serial1.begin(115200); // Inicjalizacja komunikacji szeregowej z ESP8266
}

void loop() {
  if (Serial1.available() > 0) {
    String command = Serial1.readStringUntil('\n'); // Odczytanie komendy z Serial1
    Serial.println("Received command: " + command); // Wypisanie komendy na konsoli 

    if (command == "moveForward") {
      forward();
    } else if (command == "moveBackward") {
      backward();
    } else if (command == "moveRight") {
      right();
    } else if (command == "moveLeft") {
      left();
    }
     else if (command == "speed1"){
      speed2 = 60;
      analogWrite(Speed_pin, speed2);
    }
    else if (command == "speed2"){
      speed2 = 120;
      analogWrite(Speed_pin, speed2);
    }
    else if (command == "speed3") {
      speed2 = 180;
      analogWrite(Speed_pin, speed2);
    }
    else if (command == "speed4"){
      speed2 = 255;
      analogWrite(Speed_pin, speed2);
    } 
    else {
      stopMotors(); // Jeśli nieznana, zatrzymaj 
    }
  }
}

// Funkcje sterujące silnikami
void forward() {
  analogWrite(LPWM_Output1, speed);
  analogWrite(RPWM_Output1, 0);
  analogWrite(LPWM_Output2, speed);
  analogWrite(RPWM_Output2, 0);
}

void backward() {
  analogWrite(LPWM_Output1, 0);
  analogWrite(RPWM_Output1, speed);
  analogWrite(LPWM_Output2, 0);
  analogWrite(RPWM_Output2, speed);
}

void right() {
  analogWrite(LPWM_Output1, speed);
  analogWrite(RPWM_Output1, 0);
  analogWrite(LPWM_Output2, 0);
  analogWrite(RPWM_Output2, speed);
}

void left() {
  analogWrite(LPWM_Output1, 0);
  analogWrite(RPWM_Output1, speed);
  analogWrite(LPWM_Output2, speed);
  analogWrite(RPWM_Output2, 0);
}

void stopMotors() {
  analogWrite(LPWM_Output1, 0);
  analogWrite(RPWM_Output1, 0);
  analogWrite(LPWM_Output2, 0);
  analogWrite(RPWM_Output2, 0);
}
