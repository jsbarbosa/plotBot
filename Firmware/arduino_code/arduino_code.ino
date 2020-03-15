#include <Servo.h>
#include <math.h>

#define TEST_MESSAGE "*IDN?"
#define TEST_ANSWER "plotBot v1.0"

// area in mm
#define X_ORIGIN 23
#define Y_ORIGIN -15
#define INNER_LENGTH 39
#define OUTER_LENGTH 45
#define DISTANCE_BETWEEN_ORIGINS 26

#define LEFT_FACTOR 0.82
#define RIGHT_FACTOR 1.20

#define Z_UP 45
#define Z_DOWN 70

#define X_MIN 10
#define X_MAX 65
#define X_RANGE X_MAX - X_MIN

#define Y_MIN 20
#define Y_MAX 75
#define Y_RANGE Y_MAX - Y_MIN


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

float get_beta(int x, int y)
{
  float r2 = x * x + y * y;
  float r = sqrt(r2);
  float theta2 = acos((r2 - INNER_LENGTH * INNER_LENGTH - OUTER_LENGTH * OUTER_LENGTH) / (2 * INNER_LENGTH * OUTER_LENGTH));

  return asin(OUTER_LENGTH * sin(theta2) / r);
}


float get_left_angle(int x, int y)
{
  x = x - X_ORIGIN;
  y = y - Y_ORIGIN;

  return atan2(y, x) + get_beta(x, y);
}

float get_right_angle(int x, int y)
{
  x = x - (X_ORIGIN + DISTANCE_BETWEEN_ORIGINS);
  y = y - Y_ORIGIN;

  return atan2(y, x) - get_beta(x, y);
}

void get_coordinates(int x, int y, float *theta_left, float *theta_right)
{
  float rad_left = get_left_angle(x, y);
  *theta_left = rad2deg(rad_left);
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

    x += X_MIN;
    y += Y_MIN;

    if((x < X_MIN) | (x > X_RANGE + X_MIN) | (y < Y_MIN) | (y > Y_RANGE + Y_MIN))
    { 
      Serial.println("ERROR");
    }
    else
    {
      get_coordinates(x, y, &theta_left, &theta_right);
  
      servo_left.write(theta_left * LEFT_FACTOR);
      servo_right.write(theta_right * RIGHT_FACTOR);
  
      if (z == 1)
      {
        servo_z.write(Z_UP);
      }
      else if (z == 0)
      {
        servo_z.write(Z_DOWN);
      }

      Serial.println("OK");
    }
    

    /*    
    if (x >= 0)
    {
      servo_left.write(theta_left * LEFT_FACTOR);
    }

    if (y >= 0)
    {
      servo_right.write(theta_right * RIGHT_FACTOR);
    }

    if (z == 1)
    {
      servo_z.write(Z_UP);
    }
    else if (z == 0)
    {
      servo_z.write(Z_DOWN);
    }

    if((theta_left == theta_right) & (theta_left == 0))
    {
      Serial.println("Error");
    }
    
    else
    {
      Serial.println("OK");
    }
    */
  }
}
