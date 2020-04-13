#include <spatialindex/SpatialIndex.h>

using namespace SpatialIndex;
using namespace std;

/* 
 * Test the Geometry
 * Nowhere near complete, but it's something
 */
int main(int, char**) {
    //define points
    double c1[2] = {1.0, 0.0};
    double c2[2] = {3.0, 2.0};
    double c3[2] = {2.0, 0.0};
    double c4[2] = {2.0, 4.0};
    double c5[2] = {1.0, 1.0};
    double c6[2] = {2.5, 3.0};
    double c7[2] = {1.0, 2.0};
    double c8[2] = {0.0, -1.0};
    double c9[2] = {4.0, 3.0};
    Point p1 = Point(&c1[0], 2); 
    Point p2 = Point(&c2[0], 2); 
    Point p3 = Point(&c3[0], 2); 
    Point p4 = Point(&c4[0], 2); 
    Point p5 = Point(&c5[0], 2); 
    Point p6 = Point(&c6[0], 2); 
    Point p7 = Point(&c7[0], 2); 
    Point p8 = Point(&c8[0], 2); 
    Point p9 = Point(&c9[0], 2); 
    
    double c3a[2] = {2.0, 3.0};
    Point p3a = Point(&c3a[0], 2); 
    
    //Now Test LineSegment intersection
    LineSegment ls1 = LineSegment(p1, p2);
    LineSegment ls2 = LineSegment(p3, p4);
    LineSegment ls3 = LineSegment(p3a, p4);

    if (!ls1.intersectsShape(ls2)) {
        cerr << "Test failed:  intersectsShape returned false, but should be true." << endl;
        cerr << ls1 << ", " << ls2 << endl;
        return 0;
    }

    if (ls1.intersectsShape(ls3)) {
        cerr << "Test failed:  intersectsShape returned true, but should be false." << endl;
        cerr << ls1 << ", " << ls3 << endl;
        return 0;
    }

    //Now LineSegment Region intersection
    Region r1 = Region(p5, p6);
    Region r2 = Region(p7, p6);
    Region r3 = Region(p8, p9);
    
    if (!r1.intersectsShape(ls1) || !ls1.intersectsShape(r1)) {
        cerr << "Test failed:  intersectsShape returned false, but should be true." << endl;
        cerr << r1 << ", " << ls1 << endl;
        return 0;
    }

    if (r2.intersectsShape(ls1) || ls1.intersectsShape(r2)) {
        cerr << "Test failed:  intersectsShape returned true, but should be false." << endl;
        cerr << r2 << ", " << ls1 << endl;
        return 0;
    }

    // This is the contains test
    if (!r3.intersectsShape(ls1) || !ls1.intersectsShape(r3)) {
        cerr << "Test failed:  intersectsShape returned false, but should be true." << endl;
        cerr << r3 << ", " << ls1 << endl;
        return 0;
    }

    return 0;
}
