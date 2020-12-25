#include <Servo.h>
#include <math.h>

#define TEST_MESSAGE "*IDN?"
#define TEST_ANSWER "plotBot v1.0"

//#define CALIBRATION

// origin points of left and right servo
// from the lower left corner
#define O1X 24
#define O1Y -25
#define O2X 49
#define O2Y -25

// length of arms
#define L1 35
#define L4 45
#define L3 17

#define L2 sqrt(pow(L4 + L3 * cos(M_PI / 4), 2) + pow(L3 * sin(M_PI / 4), 2))

// calibration of servos
#define LEFT_ZERO 35
#define RIGHT_ZERO 20

#define LEFT_FACTOR 1.05
#define RIGHT_FACTOR 1.20

#define Z_UP 45
#define Z_DOWN 70

//#define X_MIN 10
//#define X_MAX 65
//#define X_RANGE X_MAX - X_MIN
//
//#define Y_MIN 20
//#define Y_MAX 75
//#define Y_RANGE Y_MAX - Y_MIN

#define LEFT_PIN 10
#define RIGHT_PIN 11
#define Z_PIN 9

Servo servo_left; 
Servo servo_right;
Servo servo_z;

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(50);
  attach_servos();
}

void attach_servos(void)
{
  servo_left.attach(LEFT_PIN);
  servo_right.attach(RIGHT_PIN);
  servo_z.attach(Z_PIN);
}

void detach_servos(void)
{
  servo_left.detach();
  servo_right.detach();
  servo_z.detach();
}

String read_command(void)
{
  String input_text = "";
  if (Serial.available() > 0)
  {
    input_text = Serial.readString();
  }
  return input_text;
}

void process_code(String input, 
                  int *x,
                  int *y,
                  int *z)
{
  char text[20];
  input.toCharArray(text, 20);
  sscanf(text, "X%d Y%d Z%d", x, y, z);  
}

float rad2deg(float rad)
{
  return rad * 180 / PI;
}

float return_angle(float a, float b, float c)
{
  return acos((a * a + c * c - b * b) / (2 * a * c));
}

void get_coordinates(int x, int y, float *theta_left, float *theta_right)
{
  // LEFT ARM
  int dx, dy;
  float c, a1, a2, hx, hy;
  
  dx = x - O1X;
  dy = y - O1Y;

  c = sqrt(dx * dx + dy * dy);
  a1 = atan2(dy, dx);
  a2 = return_angle(L1, L2, c);

  *theta_left = rad2deg(a1 + a2);
  
  // RIGHT ARM

  a2 = return_angle(L2, L1, c);
  hx = x + L3 * cos(a1 - a2 + M_PI / 4 + M_PI); // PI / 4 angle of pen holder 
  hy = y + L3 * sin(a1 - a2 + M_PI / 4 + M_PI);

  dx = hx - O2X;
  dy = hy - O2Y;

  c = sqrt(dx * dx + dy * dy);
  a1 = atan2(dy, dx);
  a2 = return_angle(L1, L4, c);

  *theta_right = rad2deg(a1 - a2);
}

void write_left(int x)
{
  servo_left.write(180 - (x * LEFT_FACTOR + LEFT_ZERO));
}

void write_right(int x)
{
  servo_right.write(x * RIGHT_FACTOR + RIGHT_ZERO);
}

void write_position(int left, int right, int z)
{
//  attach_servos();
  
  write_left(left);
  write_right(right);
  servo_z.write(z);

//  delay(250);

//  detach_servos();
}

void loop()
{
  #ifdef CALIBRATION
  write_position(0, 0, Z_UP);
  delay(2000);
  write_position(90, 90, Z_UP);
  delay(2000);

  #else  
  String input = read_command();
  if(input == TEST_MESSAGE)
  {
    Serial.println(TEST_ANSWER);
  }

  else if(input != "")
  {
    int x, y, z;
    float theta_left, theta_right;
        
    process_code(input, &x, &y, &z);

//    x += X_MIN;
//    y += Y_MIN;
//
//    if((x < X_MIN) | (x > X_RANGE + X_MIN) | (y < Y_MIN) | (y > Y_RANGE + Y_MIN))
//    { 
//      Serial.println("ERROR");
//    }
//    else
//    {
      get_coordinates(x, y, &theta_left, &theta_right);
  
      write_left(theta_left);
      write_right(theta_right);
  
      if (z == 1)
      {
        servo_z.write(Z_UP);
      }
      else if (z == 0)
      {
        servo_z.write(Z_DOWN);
      }

      Serial.println("OK");
//    }
  }
  #endif
}
