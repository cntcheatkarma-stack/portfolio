// gps_set_9600.ino
// Reconfigure an ATGM336H GPS module to 9600 baud (HaleHound reads GPS at a
// fixed 9600). The GPS stays connected to the CYD's UART0 (GPIO 1/3).
//
// 1. Flash this sketch to the CYD.
// 2. Power-cycle the GPS module.
// 3. Re-flash HaleHound.
//
// If the setting reverts after a full power-down, the module's backup cell is
// flat: leave it powered to charge, or replace it with a rechargeable ML/LIR
// cell (never a plain CR2032 in a charging slot).

void setup() {
  int bauds[] = {115200, 57600, 38400, 19200, 9600};
  for (int i = 0; i < 5; i++) {
    Serial.begin(bauds[i]);
    delay(300);
    Serial.println("$PCAS01,1*1D"); // set 9600
    Serial.flush(); delay(300);
    Serial.end();   delay(100);
  }
  Serial.begin(9600); delay(300);
  Serial.println("$PCAS00*01");     // save config
}

void loop() {}
