#include <Servo.h>
#include <math.h>

#define TEST_MESSAGE "*IDN?"
#define TEST_ANSWER "plotBot v1.0"

// area in mm
#define X_ORIGIN 22
#define Y_ORIGIN -26
#define INNER_LENGTH 41
#define OUTER_LENGTH 44
#define DISTANCE_BETWEEN_ORIGINS 24

#define LEFT_FACTOR 0.82
#define RIGHT_FACTOR 1.20

Servo servo_left; 
Servo servo_right;
Servo servo_z;

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(50);

  servo_left.attach(10);
  servo_right.attach(11);
  servo_z.attach(9);

  servo_z.write(0);
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

float get_left_angle(int x, int y)
{
  x = x - X_ORIGIN;
  y = y - Y_ORIGIN;

  float r2 = x * x + y * y;
  float r = sqrt(r2);
  float theta2 = acos((r2 - INNER_LENGTH * INNER_LENGTH - OUTER_LENGTH * OUTER_LENGTH) / (2 * INNER_LENGTH * OUTER_LENGTH));

  return asin(OUTER_LENGTH * sin(theta2) / r) + atan2(y, x);
}

float get_right_angle(int x, int y)
{
  x = x - (X_ORIGIN + DISTANCE_BETWEEN_ORIGINS);
  y = y - Y_ORIGIN;

  float r2 = x * x + y * y;
  float r = sqrt(r2);
  float theta2 = acos((r2 - INNER_LENGTH * INNER_LENGTH - OUTER_LENGTH * OUTER_LENGTH) / (2 * INNER_LENGTH * OUTER_LENGTH));

  return atan2(y, x) - asin(OUTER_LENGTH * sin(theta2) / r);
}

void get_coordinates(int x, int y, float *theta_left, float *theta_right)
{
  *theta_left = rad2deg(get_left_angle(x, y));
  *theta_right = rad2deg(get_right_angle(x, y));
}

void loop()
{
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

    get_coordinates(x, y, &theta_left, &theta_right);
    
    if (x >= 0)
    {
//      servo_left.write(x * LEFT_FACTOR);
      servo_left.write(theta_left * LEFT_FACTOR);
    }

    if (y >= 0)
    {
//      servo_right.write(y * RIGHT_FACTOR);
      servo_right.write(theta_right * RIGHT_FACTOR);
    }

    if (z == 1)
    {
      servo_z.write(50);
    }
    else if (z == 0)
    {
      servo_z.write(60);
    }
    
    if((x != -1) | (y != -1) | (z != -1))
    {
      char message[24];
      
      sprintf(message, "OK left: %d right: %d", (int) theta_left, (int) theta_right);
      Serial.println(message);
    }
  }
}
