#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED display SPI pin configuration
#define OLED_MOSI   D7
#define OLED_CLK    D5
#define OLED_DC     D2
#define OLED_CS     D8
#define OLED_RESET  D4
Adafruit_SSD1306 display(OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);

String previousText = ""; // Variable to store the previous text
String incomingText; // Variable to store the incoming text


// JOY STICK CONFIG
#define JOY_X A0 // Joystick X-axis
#define JOY_SW D3 // Joystick switch
int threshold = 200; // Adjust this value based on your joystick's sensitivity

int lastJoyX = 0;
int selectedItem = 0;
bool buttonPressed = false;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;


// Function to calculate the width of a string in pixels
int getStringWidth(String str) {
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(str, 0, 0, &x1, &y1, &w, &h); // Calculate the bounds of the string
  return w;
}


// Function to display a centered menu on the OLED with a selection indicator
void showMenu(String menuItems[], int itemCount, int selectedItem) {
  display.clearDisplay(); // Clear the display buffer
  display.setTextSize(1); // Set text size
  display.setTextColor(WHITE); // Set text color

  int lineHeight = 8; // Height of each line of text
  int startY = (display.height() - (itemCount * lineHeight)) / 2; // Start position for Y to center the menu

  for (int i = 0; i < itemCount; i++) {
    int strWidth = getStringWidth(menuItems[i]);
    int startX = (display.width() - strWidth) / 2; // Calculate X position to center the string

    // If this is the selected item, draw an indicator
    if (i == selectedItem) {
      display.setCursor(startX - 10, startY + (i * lineHeight)); // Position cursor for the indicator
      display.print(">"); // Print an arrow as the indicator
      display.setTextColor(BLACK, WHITE); // Highlight selected item
    } else {
      display.setTextColor(WHITE); // Normal colors for other items
      display.setCursor(startX, startY + (i * lineHeight)); // Position cursor for menu item
    }

    display.println(menuItems[i]); // Display each menu item
  }

  display.display(); // Actually draw the text on the display
}

// Define menu items
String menuItems[] = {"Item 1", "Item 2", "Item 3", "Item 4"};
int itemCount = 4; // Number of items in the menu



void setup() {
  Serial.begin(9600); // Start serial communication at 9600 baud
  pinMode(JOY_X, INPUT);
  pinMode(JOY_SW, INPUT_PULLUP); // Enable internal pull-up resistor
  // Initialize OLED display with SPI
  if (!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  display.clearDisplay(); // Clear the buffer
  display.setCursor(0,0);
  display.setTextSize(1); // Set text size
  display.setTextColor(WHITE); // Set text color
    // Display the menu
  showMenu(menuItems, itemCount, selectedItem);
  display.display();
}



void loop() {
  int currentJoyX = analogRead(JOY_X);
  int joyDelta = currentJoyX - lastJoyX;

  if (abs(joyDelta) > threshold) { // threshold to avoid noise
    if (joyDelta > 0) {
      selectedItem++;
    } else {
      selectedItem--;
    }
    selectedItem = max(0, min(selectedItem, itemCount - 1)); // Keep within bounds
    showMenu(menuItems, itemCount, selectedItem);
    lastJoyX = currentJoyX;
  }

  // Debounce the joystick button press
  if (!digitalRead(JOY_SW)) {
    if ((millis() - lastDebounceTime) > debounceDelay) {
      // Button pressed, update the display
      display.clearDisplay();
      display.setCursor(0, 0);
      display.print("Title"); // Display the default text
      display.display();
      lastDebounceTime = millis();
    }
  }












  if (Serial.available()) {
      // Read the incoming string
      incomingText = Serial.readStringUntil('\n');

      // Check if the incoming text is different from the previous text
      if (incomingText != previousText) {
          // Set cursor position to the top-left corner
          display.setCursor(0,0);
          display.clearDisplay(); // Clear the display
          display.print(incomingText); // Display the incoming string
          display.display(); // Actually draw the text on the display
          previousText = incomingText; // Update the previous text
      }
  }
}
