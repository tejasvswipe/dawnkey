// DAWNKEY — parametric BLARE enclosure, designed around a 94 x 90 mm PCB.
// Units: mm. Print parts separately; verify the actual TFT, holder and switch before final print.
$fn = 48;
part = "assembly"; // base, top, bezel, battery_pod, battery_door, accents, text, assembly

// Main electronics envelope
PCB_X = 7.0;
PCB_Y = 8.0;
PCB_W = 94.0;
PCB_H = 90.0;
CASE_W = 108.0;
CASE_D = 132.0;
BASE_H = 15.5;
TOP_T = 2.4;
WALL = 2.4;
FLOOR = 2.4;
PCB_BOTTOM = 7.8;
PLATE_Z = BASE_H;

module round_slab(w,d,h,r,z=0) {
  translate([w/2,d/2,z])
    linear_extrude(height=h)
      offset(r=r) square([w-2*r,d-2*r], center=true);
}

module board_hole(x,y) {
  translate([PCB_X+x, PCB_Y+y, -0.2]) cylinder(d=3.4,h=22);
}

module pcb_posts() {
  for (p=[[4.5,4.5],[89.5,4.5],[4.5,85.5],[89.5,85.5]]) {
    translate([PCB_X+p[0], PCB_Y+p[1], FLOOR])
      difference() {
        cylinder(d=9.0,h=PCB_BOTTOM-FLOOR);
        // M3 heat-set insert pocket, open at the post top; confirm insert dimensions.
        translate([0,0,PCB_BOTTOM-FLOOR-4.8]) cylinder(d=4.6,h=5.1);
      }
  }
}

module base_shell() {
  difference() {
    round_slab(CASE_W,CASE_D,BASE_H,8.0,0);
    translate([WALL,WALL,FLOOR])
      round_slab(CASE_W-2*WALL,CASE_D-2*WALL,BASE_H-FLOOR+0.3,5.6,0);
    // Large USB/service clearance at the XIAO side. Final slot position depends on
    // the actual XIAO USB-C orientation and is intentionally generous for prototype fit.
    translate([-0.3, PCB_Y+57, 6.2]) cube([WALL+0.6,25,8.0]);
    // Pass-through from AA pod to PCB battery input harness.
    translate([CASE_W-1.0,71,5.5]) cube([3.0,10,6.0]);
  }
  pcb_posts();
  // Short internal rails support the TFT module below its top bezel.
  for (x=[15,89]) {
    translate([x,98.0,11.0]) cube([4.0,25.0,2.0]);
  }
}

module top_plate() {
  difference() {
    round_slab(CASE_W,CASE_D,TOP_T,8.0,PLATE_Z);
    // Four PCB M3 screws share the board mounting pattern and thread into insert posts.
    for (p=[[4.5,4.5],[89.5,4.5],[4.5,85.5],[89.5,85.5]])
      translate([PCB_X+p[0],PCB_Y+p[1],PLATE_Z-0.2]) cylinder(d=3.4,h=TOP_T+0.5);
    // MX plate apertures: nominal 14 mm; 0.2 mm clearance built in.
    for (x=[16.425,35.475,54.525,73.575])
      for (y=[13.5,32.55,51.6])
        translate([PCB_X+x,PCB_Y+y,PLATE_Z-0.2])
          linear_extrude(height=TOP_T+0.5)
            offset(r=0.6) square([13.0,13.0],center=true);
    // ST7789 visible window and underside pocket for its 76 x 28.4 mm PCB.
    translate([54,114,PLATE_Z-0.2]) cube([72,20.5,TOP_T+0.5],center=true);
    translate([54,114,PLATE_Z-0.1]) cube([77.0,29.4,1.25],center=true);
    // Acoustic vent array over the piezo area.
    for (x=[34,39,44,49])
      translate([x,90,PLATE_Z-0.2]) hull() {
        translate([0,-3,0]) cylinder(d=2.3,h=TOP_T+0.5);
        translate([0, 3,0]) cylinder(d=2.3,h=TOP_T+0.5);
      }
    // Two angled cyber-deck accent slots, filled with separate neon parts.
    for (x=[18,23,28])
      translate([x,82,PLATE_Z+TOP_T-0.75]) rotate([0,0,-28]) cube([1.4,12,1.7],center=true);
  }
  // Short display shelf lips capture the display PCB from behind; tune to the real module.
  for (x=[15,89])
    translate([x,98.0,PLATE_Z-1.4]) cube([4.0,25.0,1.5]);
}

module display_bezel() {
  // Raised octagonal visor, separate print; an internal shelf keeps the panel behind the aperture.
  difference() {
    translate([12,96,0]) round_slab(84,36,3.0,5.0,PLATE_Z+TOP_T-0.2);
    translate([54,114,PLATE_Z+TOP_T+1.3]) cube([73.0,21.5,4.6],center=true);
  }
}

// Sidecar pod gives a standard wired 2xAA holder a separate, serviceable compartment.
// Nominal cavity 66 x 37 x 19 mm. Measure the purchased holder before printing.
POD_X=110;
POD_Y=54;
POD_W=72;
POD_D=45;
POD_H=21;

module battery_pod() {
  difference() {
    round_slab(POD_W,POD_D,POD_H,9.0,0);
    translate([WALL,WALL,2.2])
      round_slab(POD_W-2*WALL,POD_D-2*WALL,POD_H-1.4,6.4,0);
    // Removable door opening; four M2.5 screw holes retain the cover.
    translate([POD_W/2,POD_D/2,-0.2]) cube([POD_W-6,POD_D-6,3.0],center=true);
    for (p=[[7,7],[POD_W-7,7],[7,POD_D-7],[POD_W-7,POD_D-7]])
      translate([p[0],p[1],-0.2]) cylinder(d=2.6,h=4.0);
    // Generic side-slot for an SPST slide switch in the holder-positive lead.
    translate([POD_W-0.5,POD_D/2,9.0]) cube([3.0,12.0,4.2],center=true);
    // Lead exit towards the main case.
    translate([-0.5,POD_D/2,5.5]) cube([3.0,10.0,6.0]);
  }
  // Internal ledges support a standard commercial two-cell holder.
  for (y=[8,POD_D-10])
    translate([6,y,2.2]) cube([POD_W-12,2.0,4.0]);
}

module battery_door() {
  translate([POD_X+POD_W/2,POD_Y+POD_D/2,0])
    difference() {
      cube([POD_W-7,POD_D-7,2.0],center=true);
      for (p=[[7,7],[POD_W-7,7],[7,POD_D-7],[POD_W-7,POD_D-7]])
        translate([p[0]-POD_W/2,p[1]-POD_D/2,-1.2]) cylinder(d=2.8,h=3.0);
    }
}

module neon_accents() {
  // Three flush-inlay slashes at the top-left edge of the name panel.
  for (i=[0:2])
    translate([18+i*5,82,PLATE_Z+TOP_T-1.35]) rotate([0,0,-28])
      cube([1.15,11.2,1.1],center=true);
}

module for_tejas() {
  // Separate black multi-material insert; print flat and place on the panel.
  translate([54,83.5,PLATE_Z+TOP_T-0.12])
    linear_extrude(height=0.75)
      text("for tejas",size=6.2,font="DejaVu Sans:style=Bold",halign="center",valign="center");
}

module key_labels() {
  labels=["1","2","3","4","5","6","7","8","9","0","S","OK"];
  xx=[16.425,35.475,54.525,73.575]; yy=[51.6,32.55,13.5];
  for (i=[0:11]) {
    c=i%4; r=floor(i/4); sz=(i<10)?3.2:2.2;
    translate([PCB_X+xx[c],PCB_Y+yy[r],PCB_BOTTOM+1.6+6.5+7.02])
      linear_extrude(height=0.38)
        text(labels[i],size=sz,font="DejaVu Sans:style=Bold",halign="center",valign="center");
  }
}

module display_graphics() {
  color("#111723") translate([18,103.75,PLATE_Z+TOP_T+0.02]) cube([72,20.5,0.25]);
  color("#10e6ec") translate([29,109,PLATE_Z+TOP_T+0.27])
    linear_extrude(height=0.16) text("07:00",size=8,font="DejaVu Sans:style=Bold");
  color("#ff4fb3") translate([67,113,PLATE_Z+TOP_T+0.27])
    linear_extrude(height=0.16) text("WAKE",size=2.5,font="DejaVu Sans:style=Bold");
}

module mock_components() {
  // Visual-only assembly stand-ins (not electrical footprints): PCB, keycaps, TFT and AA cells.
  color("#145b68") translate([PCB_X,PCB_Y,PCB_BOTTOM]) cube([PCB_W,PCB_H,1.6]);
  for (x=[16.425,35.475,54.525,73.575]) for (y=[13.5,32.55,51.6]) {
    color("#252525") translate([PCB_X+x-6.5,PCB_Y+y-6.5,PCB_BOTTOM+1.6]) cube([13,13,5]);
    color("#f5f1ed") translate([PCB_X+x-8.5,PCB_Y+y-8.5,PCB_BOTTOM+6.5]) cube([17,17,7]);
  }
  // TFT mock-up sits in the underside pocket; glass and sample glyphs show through the window.
  color("#171923") translate([16,99.8,PLATE_Z-0.7]) cube([76,28.4,1.2]);
  for (y=[POD_Y+12,POD_Y+33])
    color("#d3d4d8") translate([POD_X+36,y,8.5]) rotate([0,90,0]) cylinder(d=14.5,h=49,center=true);
}

module assembly() {
  color("#e9edf2") base_shell();
  color("#f7f7f4") top_plate();
  color("#191b22") display_bezel();
  color("#272934") translate([POD_X,POD_Y,0]) battery_pod();
  color("#25262b") battery_door();
  color("#11d9e8") neon_accents();
  color("#050505") for_tejas();
  mock_components();
  color("#050505") key_labels();
  display_graphics();
}

if (part=="base") color("#e9edf2") base_shell();
else if (part=="top") color("#f7f7f4") top_plate();
else if (part=="bezel") color("#191b22") display_bezel();
else if (part=="battery_pod") color("#272934") translate([POD_X,POD_Y,0]) battery_pod();
else if (part=="battery_door") color("#25262b") battery_door();
else if (part=="accents") color("#11d9e8") neon_accents();
else if (part=="text") color("#050505") for_tejas();
else if (part=="key_labels") color("#050505") key_labels();
else assembly();
