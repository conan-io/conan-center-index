/**
 *  Starfield Simulation
 *  Author: Maks Makuta
 *  URLs:
 *      Part 1: https://youtube.com/shorts/Bk5O7-3xIfw
 *      Part 2: https://youtube.com/shorts/IS6_apBewlI
 */

#include <processing.h>

float speed;

class Star{
  private:
    float x,y,z,pz;
  public:
    Star(){
      this->x = random(-width,width);
      this->y = random(-height,height);
      this->z = random(width);
      this->pz = z;
    }

    void update(){
      this->z -= speed;
      if(this->z < 1.f){
        this->z = width;
        this->x = random(-width,width);
        this->y = random(-height,height);
        this->pz = z;
      }
    }

    void show(){
      fill(255);

      float sx = map<float>(this->x / this->z,0,1,0, width);
      float sy = map<float>(this->y / this->z,0,1,0,height);

      float r = map<float>(this->z,0,width,16,0);
      circle(sx,sy,r);

      float zx = map<float>(this->x / this->pz,0,1,0, width);
      float zy = map<float>(this->y / this->pz,0,1,0,height);

      this->pz = z;

      stroke(255);
      line(zx,zy,sx,sy);
    }

};

std::vector<Star> stars;

void setup(){
    size(640,480);
    for(int a = 0;a < 100;a++)
      stars.push_back(Star());
}

void draw(){
  speed = map<float>(mouseX,0,width,0.f,50.f);
  background(0);
  translate(width/2,height/2);

  for(int a = 0;a < stars.size();a++){
    stars[a].update();
    stars[a].show();
  }

}
