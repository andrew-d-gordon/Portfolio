/*
This file is to be used in tandem with the Rocket.pde file, run through the Processing Application
Origin rocket class and file provided by Charlie McDowell from Canvas.
This program is by Andrew Gordon and Nick Shekelle.
Our Program is a game where one must land the rocket on the displayed platform
without tilting the rocket too much, managing speed with thrust (thrust activated
when pressing UPARROW, if you exceed .35 yVelocity or .2 abs(xVelocity) when
hitting platform you will crash), turning with lft/rt arrows, and not running out of fuel before 
you reach the platform.  Note: Each time program is run, platform changes position
horizontally and vertically, as well as change in width.
*/

void setup() {
  size(500, 500);
  rocket = new Rocket(random(width/2-80,width/2+80), height/2-100);
}

// Declares the rocket class
Rocket rocket;

/* Draws blackish background, calls all rocket methods
in rocket class,as well as the adjustControls method */
void draw() {
  rocket.sSky(2);
  adjustControls(rocket);
  rocket.drawGround();
  rocket.update();
  rocket.fuelDisplay(20, 20);
  rocket.altitude(20,40);
  rocket.RocketVel(20,60);
}

/*
  Control the rocket using mouseY for thrust and 'a' or left-arrow for rotating
 counter-clockwise and 'd' or right-arrow for rotating clockwise.
 It takes a single parameter, which is the rocket being controlled.
 */
void adjustControls(Rocket rocket) {
  // control thrust with the up arrow
  rocket.setThrust(0);
  if (keyPressed) {
    if (keyCode==UP) {
      rocket.setThrust(100);
    }
  }
  // allow for right handed control with arrow keys or
  // left handed control with 'a' and 'd' keys

  // right hand rotate controls
  if (keyPressed) {
    if (key == CODED) { // tells us it was a "special" key
      if (keyCode == RIGHT) {
        rocket.rotateRocket(1);
      } else if (keyCode == LEFT) {
        rocket.rotateRocket(-1);
      }
    }
    // left hand rotate controls
    else if (key == 'a') {
      rocket.rotateRocket(-1);
    } else if (key == 'd') {
      rocket.rotateRocket(1);
    }
  }
}
