#include <cstdlib>
#include "clipper2/clipper.h"

using namespace std;
using namespace Clipper2Lib;

void TestingZ_Double();

// use the Z callback to flag intersections by setting z = 1;

class MyClass {
public:

  // Point64 callback - see TestingZ_Int64()
  void myZCB(const Point64& e1bot, const Point64& e1top,
    const Point64& e2bot, const Point64& e2top, Point64& pt)
  {
    pt.z = 1;
  }

  // PointD callback - see TestingZ_Double()
  void myZCBD(const PointD& e1bot, const PointD& e1top,
    const PointD& e2bot, const PointD& e2top, PointD& pt)
  {
    pt.z = 1;
  }
};

int main(int argc, char* argv[])
{
  TestingZ_Double();
}
void TestingZ_Double()
{
  PathsD subject, solution;
  MyClass mc;
  ClipperD c;

  subject.push_back(MakePathD({ 100, 50, 10, 79, 65, 2, 65, 98, 10, 21 }));
  c.AddSubject(subject);
  c.SetZCallback(
    std::bind(&MyClass::myZCBD, mc, std::placeholders::_1,
      std::placeholders::_2, std::placeholders::_3,
      std::placeholders::_4, std::placeholders::_5));
  c.Execute(ClipType::Union, FillRule::NonZero, solution);
}
