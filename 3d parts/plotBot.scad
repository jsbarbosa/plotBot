plate_height = 3;
xy_thickness = 0.8;

arm_diameter = 12;
arm_length = 45;
arm_width = 9;

arm_pen_diameter = 20;
pen_tip_diameter = 6;

screw_diameter = 3.2;

pen_height = 27;

nut_diameter = 7;
nut_thickness = 3;

$fn = 50;

module Arm()
{
    distance = (arm_diameter + arm_pen_diameter) / 2 + 1;
            
    x = - distance * cos(45);
    y = arm_length / 2 + distance * sin(45);
    
    difference()
    {
        union()
        {
            cube([arm_width, arm_length, plate_height],
                  center=true);
            
            translate([0, arm_length / 2, 0])
            cylinder(d=arm_diameter,
                         h=plate_height,
                         center=true);
            
            translate([0, -arm_length / 2, 0])
            cylinder(d=arm_diameter,
                     h=plate_height,
                     center=true);
            
            translate([x, y, pen_height / 2])
            PenHolder();
            
            translate([-1, arm_length / 2 - distance * sin(45) / 2, -plate_height / 2])
            rotate([0, 0, 45])
            cube([arm_width, distance, plate_height]);
        }
        
        translate([0, arm_length / 2, 0])
        cylinder(d=screw_diameter,
             h=1.5 * plate_height,
             center=true);
        
        translate([0, -arm_length / 2, 0])
        cylinder(d=screw_diameter,
             h=1.5 * plate_height,
             center=true);
    }
    
}

module NutHolder(diameter)
{
    rotate([90, 0, 0])
    difference()
    {
        cylinder(d=diameter,
                  h=2*nut_thickness,
                  center=true);
        
        translate([0, 0, -nut_thickness / 2])
        cylinder(d=nut_diameter,
                 h=2*nut_thickness,
                 center=true,
                 $fn=6);
    }
}


module PenHolder(wall_thickness = 1.2)
{
    diameter = nut_diameter + 2 * xy_thickness;
    nut_height = 0.75 * (pen_height + plate_height - diameter) / 2;
    
    difference()
    {
        union()
        {
            cylinder(d=arm_pen_diameter,
                     h=pen_height + plate_height,
                     center=true);
            
            for(i = [0: 2])
            {
                rotate([0, 0, 125 * i])
                translate([0, arm_pen_diameter / 2, nut_height])
                NutHolder(diameter);
            }
        }
    
        // inner cylinder
        translate([0, 0, plate_height])
        cylinder(d=arm_pen_diameter - wall_thickness * 2,
                 h=pen_height + plate_height,
                 center=true);
    
        // pen tip cylinder
        translate([0, 0, -pen_height / 2])
        cylinder(d=pen_tip_diameter,
                 h=1.1 * plate_height,
                 center=true);
        
        for(i = [0: 2])
        {
            rotate([0, 0, 125 * i])
            translate([0, arm_pen_diameter / 2, nut_height])
            rotate([90, 0, 0])
            cylinder(d=screw_diameter,
                     h=1.2 * wall_thickness);
            
        }        
    }
    
    
    
}

Arm();