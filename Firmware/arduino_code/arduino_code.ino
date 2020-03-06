#include <Servo.h>

#define TEST_MESSAGE "*IDN?"
#define TEST_ANSWER "plotBot v1.0"

Servo servo_x1; 
Servo servo_x2;
Servo servo_z;

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(50);

  servo_x1.attach(10);
  servo_x2.attach(11);
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
    x = y = z = -1;
    process_code(input, &x, &y, &z);

    if (x >= 0)
    {
      servo_x1.write(x);
    }

    if (y >= 0)
    {
      servo_x2.write(y);
    }

    if (z >= 0)
    {
      servo_z.write(z);
    }
    
    if((x != -1) | (y != -1) | (z != -1))
    {
      Serial.println("OK");
    }
  }
}
