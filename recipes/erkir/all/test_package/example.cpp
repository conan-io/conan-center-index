#include <erkir/sphericalpoint.h>
#include <erkir/ellipsoidalpoint.h>
#include <erkir/cartesianpoint.h>

int main(int argc, char **argv)
{
  // Calculate great-circle distance between two points.
  erkir::spherical::Point p1{ 52.205, 0.119 };
  erkir::spherical::Point p2{ 48.857, 2.351 };
  auto d = p1.distanceTo(p2); // 404.3 km
  
  // Get destination point by given distance (shortest) and bearing from start point.
  erkir::spherical::Point p3{ 51.4778, -0.0015 };
  auto dest = p3.destinationPoint(7794.0, 300.7); // 51.5135°N, 000.0983°W
  
  // Convert a point from one coordinates system to another.
  erkir::ellipsoidal::Point pWGS84(51.4778, -0.0016, 0, erkir::ellipsoidal::Datum::Type::WGS84);
  auto pOSGB = pWGS84.toDatum(erkir::ellipsoidal::Datum::Type::OSGB36); // 51.4778°N, 000.0000°E

  // Convert to Cartesian coordinates.
  auto cartesian = pWGS84.toCartesianPoint();

  // Convert Cartesian point to a geodetic one.
  auto geoPoint = cartesian->toGeoPoint();

  return 0;
}
