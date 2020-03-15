width = 70;
length = 24;
height = 5;

thick = 0.8;

diameter = 6;

difference()
{
    cube([width + thick * 2, length + thick * 2, height], center=true);
    translate([0, 0, thick])
    cube([width, length, height], center=true);
    
    cylinder(d=diameter, h=1.1 * height, center=true, $fn=25);
}