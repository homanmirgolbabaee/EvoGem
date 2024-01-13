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




// Additional global variables for the game
bool gameActive = false;
int playerX; // Player's horizontal position
int playerWidth = 10; // Width of the player
int bulletY; // Y position of the bullet (if -1, no bullet is on the screen)
int objectX, objectY; // Position of the falling object
int objectSize = 10; // Size of the falling object
int score = 0; // Player's score



int readJoystickX() {
  static unsigned long lastReadTime = 0;
  static int lastReadValue = analogRead(JOY_X);

  if (millis() - lastReadTime > debounceDelay) {
    lastReadValue = analogRead(JOY_X);
    lastReadTime = millis();
  }

  return lastReadValue;
}

int playerLives = 3; // Number of lives the player has

void startGame() {
  gameActive = true;
  playerX = display.width() / 2 - playerWidth / 2;
  bulletY = -1;
  objectY = -1;
  score = 0;
  playerLives = 3; // Reset lives when game starts
}

void updateGame() {
  // Read joystick X-axis
  int currentJoyX = analogRead(JOY_X);
  int joyXCenter = 512; // Center value for the joystick

  // Calculate the difference from the center position
  int joyDifference = currentJoyX - joyXCenter;

  // Determine the movement speed based on joystick position
  int movementSpeed = 0;
  if (abs(joyDifference) > threshold) {
    movementSpeed = map(abs(joyDifference), threshold, 1023 - threshold, 1, 5);
    if (joyDifference > 0) {
      playerX += movementSpeed; // Move right
    } else {
      playerX -= movementSpeed; // Move left
    }

    // Keep the player within the screen bounds
    playerX = constrain(playerX, 0, display.width() - playerWidth);
  }

  // Shoot a bullet
  if (digitalRead(JOY_SW) == LOW && bulletY < 0) {
    bulletY = display.height() - 10; // Start position of the bullet
  }

  // Update bullet position
  if (bulletY >= 0) {
    bulletY -= 4;
    if (bulletY < 0) bulletY = -1; // Bullet is off the screen
  }

  // Increase falling speed based on score
  int fallingSpeed = 1 + score / 2.5; // Increase speed every 5 points

  // Move the falling object
  if (objectY < 0) {
    objectY = 0;
    objectX = random(0, display.width() - objectSize);
  } else {
    objectY += fallingSpeed;
  }

  // Check collision with bullet
  if (bulletY >= 0 && bulletY < objectY + objectSize && 
      playerX < objectX + objectSize && playerX + playerWidth > objectX) {
    score++;
    objectY = -1; // Reset the falling object
    bulletY = -1; // Remove the bullet
  }

  // Check if the object reached the player
  if (objectY >= display.height() - 10 && objectX >= playerX && objectX <= playerX + playerWidth) {
    playerLives--;
    objectY = -1; // Reset the falling object

    if (playerLives <= 0) {
      gameActive = false; // End the game if no lives left
      delay(2000);
      startGame(); // Restart the game
    }
  }

  // Redraw the game screen
  display.clearDisplay();

  // Draw the player
  display.fillRect(playerX, display.height() - 10, playerWidth, 5, WHITE);

  // Draw the bullet
  if (bulletY >= 0) {
    display.drawLine(playerX + playerWidth / 2, bulletY, playerX + playerWidth / 2, bulletY + 3, WHITE);
  }

  // Draw the falling object
  if (objectY >= 0) {
    display.fillRect(objectX, objectY, objectSize, objectSize, WHITE);
  }

  // Display the score
  display.setCursor(0, 0);
  display.print("Score: ");
  display.print(score);

  // Display the lives
  display.setCursor(display.width() - 50, 0);
  display.print("Lives: ");
  display.print(playerLives);

  display.display(); // Refresh the display


  
}

// Display the lives
void showLives() {
  display.setCursor(display.width() - 50, 0);
  display.print("Lives: ");
  display.print(playerLives);
}


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
  display.setCursor(0, 0);
  display.setTextSize(1); // Set text size
  display.setTextColor(WHITE); // Set text color

  playerX = display.width() / 2 - playerWidth / 2; // Initialize player position
  objectY = -1; // Initialize object position

  gameActive = true; // Start the game immediately
}
void loop() {
  if (!gameActive) {
    int joyX = readJoystickX();

    // Navigate through the menu
    if (joyX > 512 + threshold) {
      selectedItem = min(selectedItem + 1, itemCount - 1);
      delay(200); // Prevent too fast navigation
    } else if (joyX < 512 - threshold) {
      selectedItem = max(selectedItem - 1, 0);
      delay(200); // Prevent too fast navigation
    }

    // Select the menu item
    if (digitalRead(JOY_SW) == LOW) {
      startGame();
    }

    showMenu(menuItems, itemCount, selectedItem);
  } else {
    updateGame(); // Update and display the game
  }
}
