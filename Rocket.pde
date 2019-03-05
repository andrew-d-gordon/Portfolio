/*
  A simple rocket class, operating in a vacuum (no friction)
 but with gravity pulling it down.
 by Charlie McDowell 
 */
class Rocket {
  /**
   Initial location of the rocket.
   @param startX - horizontal location
   @param startY - vertical location
   */
  Rocket(float startX, int startY) {
    x = startX;
    y = startY;
  }

  // Setting star filled sky background
  void sSky(int s) {
    background(0,0,30);
    noStroke();
    fill(255,240,180);
    randomSeed(1000000);
    for (int i=0; i<1200; i++) {
      ellipse(random(width), random(height), s, s);
    }
  }

  /**
   Decrease the thrust by the specified amount where decreasing by 100 will
   immediately reduce thrust to zero.  Also sets certain amount of fuel when thrust is applied.
   */
  void setThrust(int amount) {
    amount = constrain(amount, 0, 100);
    thrust = MAX_THRUST*amount/200;
    if (thrust < 0) thrust = 0;
    if (fuelAmt==0) thrust=0;
    if (thrust>0) {
      fuelAmt-=1;
    } else {
      return;
    }
  }

  // Displays amount of fuel in upper left
  void fuelDisplay(int fuelx, int fuely) {
    textSize(15);
    fill(255, 180, 0);
    text("Fuel Tank: " + fuelAmt + " gal. / " + ((fuelAmt/fuelPerc)*100) + " %", fuelx-15, fuely);
  }

  // Displays altitude based on Y position in upper left
  void altitude(int altTX, int altTY) {
    textSize(15);
    fill(255, 150, 0);
    text("Altitude: " + (500-y), altTX-15, altTY);
  }

  // Displays horizontal and vertical velocity of rocket (x100) in upper left
  void RocketVel(int rx, int ry) {
    fill(255, 120, 0);
    textSize(15);
    text("Vertical Velocity: " + yVel*100, rx-15, ry);
    fill(255, 90, 0);
    text("Horizontal Velocity: " + abs(xVel), rx-15, ry+20);
  }
  /**
   Rotate the rocket positive means right or clockwise, negative means
   left or counter clockwise.
   */
  void rotateRocket(int amt) {
    tilt = tilt + amt*TILT_INC;
  }

  /* This method draws the rocket top, body, and bottom
  (me and nick used a similar rocket in our program 4
  which we were partners for) */
  void drawRocket() {
    fill(155, 0, 0);
    triangle(rocketX-10, bY+1, rocketX+10, bY+1, rocketX+0, bY-20);
    fill(190);
    rect(rocketX-5, bY-10, 10, -25);  
    fill(255);
    triangle(rocketX-10, bY-35, rocketX+10, bY-35, rocketX+0, bY-50);
  }
  
  /* This method determines whether or not the rocket has more
  fuel, and stops the program if the rocket has run out of fuel. */
  void noMoreFuel() {
    if (fuelAmt==0) {
      textSize(19);
      text("You ran out of fuel and life support, everyone died :(", width/2-245, height/2-10);
      textSize(15);
      text("Restart program to try again.", width/2-100, height/2+20);
      xVel=0;
      yVel=0;
    }
  }
    
  /* This set of if statements determines whether or not the rocket has safely landed or tragically crashed.
  If the rockets' xVel is <= to .2, yVel is <= .35, and it is less than +-PI/8 radians from vertical, and it 
  lands within the x bounds of the platform then it lands safely.
  If the rockets' xVel is greater than .2, yVel is greater than .35, it's rotated more than +-PI/8 radians from vertical,
  or it misses the platform, it crashes*/
  void rocketLandOrCrash() {
    if (height-y<=height-gY) {
      noLoop();
      if (yVel<=yVelCap && abs(xVel)<=xVelCap && tilt>=PI/2-PI/8 && tilt<=PI/2+PI/8 && abs(xVel)<=.2 && x<=(gX+gW) && x>=gX) {
        text("You Landed Safely", width/2-130, height/2-10);
        stroke(0);
        textSize(15);
        text("Restart program to go again!", width/2-100, height/2+20);
        yVel=0;
        xVel=0;
      } else if (yVel>=.35 || tilt<=PI/2-PI/8 || tilt>=PI/2+PI/8 || abs(xVel)>=.2 || x>=gX+gW || x<=gX) {
        text("CRASH", width/2-40, height/2-10);
        textSize(15);
        text("Restart program to try again...", width/2-100, height/2+20);
        yVel=.3;
        xVel=.01;
      }
    }
  }
  
  // Draw the rocket thrust "flames", which get bigger when thrust is applied
  void rocketFlames() {
    fill(255, 0, 0);
    stroke(255, 155, 0);
    line(flameX, flameY, flameX, thrust * FLAME_SCALE);
    line(flameX-3, flameY, flameX-3, thrust * FLAME_SCALE);
    line(flameX-5, flameY, flameX-6, thrust*FLAME_SCALE);
    line(flameX+3, flameY, flameX+4, thrust*FLAME_SCALE);
  }
  
  /* Draws the landing platform at x gX, y gY, and width gW, 
  changes length of pole up to platform each run of program. */
  void landingS() {
    fill(100);
    noStroke();
    rect((gX+gW/2)-7,gY+10,14,(height-25)-gY);
    fill(255);
    stroke(255);
    rect(gX, gY, gW, gH);
  }
  
  // This draws the ground at bottom of scene
  void drawGround() {
    fill(#F5C254);
    noStroke();
    rect(0,height-20,width,20);
  }
  /**
   Adjust the position and velocity, and call methods which draw the rocket
   + methods which determine if the rocket has crashed/ran out of fuel.
   */
  void update() {
    x = x + xVel;
    y = y + yVel;
    xVel = xVel - cos(tilt)*thrust;
    yVel = yVel - sin(tilt)*thrust + GRAVITY;
    // to make it more stable set very small values to 0
    if (abs(xVel) < 0.00005) xVel = 0;
    if (abs(yVel) < 0.00005) yVel = 0;
    // draw it
    pushMatrix();
    noStroke();
    translate(x, y);
    rotate(tilt - PI/2); 
    // calls drawRocket method in Rocket class
    drawRocket();
    // calls rocketFlames method in Rocket class
    rocketFlames();
    popMatrix();
    // calls landingS method in Rocket class
    landingS();
    textSize(30);
    fill(255, 0, 0);
    //Calls rocketCrash method in Rocket class
    rocketLandOrCrash();
    // Calls noMoreFuel method in Rocket class
    noMoreFuel();
  }

  /* Down here we have all the rocket class variables used throughout the program.
   Notably gX and gW is set randomly so that the landing platform varies in horizontal location
   and width each time it is run. Here is also where one adjusts how much fuel the rocket has.*/
  private float x, y, xVel, yVel, thrust = GRAVITY, tilt = HALF_PI;
  float fuelAmt=700;
  float fuelPerc=fuelAmt;
  float rocketX=0;
  float rocketY=0;
  float flameX=0;
  float flameY=0;
  float gY=random(400, 450);
  float gH=10;
  float gX=random(0, 430);
  float gW=random(40, 80);
  float bY;
  float yVelCap=.35;
  float xVelCap=.2;

  // the values below were arrived at by trial and error
  // for something that had the responsiveness desired
  // I multiplied gravity by 1.2 here.
  static final float GRAVITY = 0.0012;
  static final float MAX_THRUST = 5*GRAVITY;
  static final float TILT_INC = 0.005;
  static final int FLAME_SCALE = 5000; // multiplier to determine how long the flame should be based on thrust
}