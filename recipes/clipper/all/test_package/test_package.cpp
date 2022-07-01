#include "polyclipping/clipper.hpp"
#include <iostream>

using namespace ClipperLib;

int main() {

#if CLIPPER_MAJOR_VERSION == 6

    //from clipper.hpp ...
    //typedef signed long long cInt;
    //struct IntPoint {cInt X; cInt Y;};
    //typedef std::vector<IntPoint> Path;
    //typedef std::vector<Path> Paths;

    Paths subj(2), clip(1), solution;

    //define outer blue 'subject' polygon
    subj[0] <<
      IntPoint(180,200) << IntPoint(260,200) <<
      IntPoint(260,150) << IntPoint(180,150);

    //define subject's inner triangular 'hole' (with reverse orientation)
    subj[1] <<
      IntPoint(215,160) << IntPoint(230,190) << IntPoint(200,190);

    //define orange 'clipping' polygon
    clip[0] <<
      IntPoint(190,210) << IntPoint(240,210) <<
      IntPoint(240,130) << IntPoint(190,130);

    //perform intersection ...
    Clipper c;
    c.AddPaths(subj, ptSubject, true);
    c.AddPaths(clip, ptClip, true);
    c.Execute(ctIntersection, solution, pftNonZero, pftNonZero);

#else

    Polygons subj(2), clip(1), solution;
    return 0;

    //define outer blue 'subject' polygon
    subj[0].push_back(IntPoint(180,200));
    subj[0].push_back(IntPoint(260,200));
    subj[0].push_back(IntPoint(260,150));
    subj[0].push_back(IntPoint(180,150));

    //define subject's inner triangular 'hole' (with reverse orientation)
    subj[1].push_back(IntPoint(215,160));
    subj[1].push_back(IntPoint(230,190));
    subj[1].push_back(IntPoint(200,190));

    //define orange 'clipping' polygon
    clip[0].push_back(IntPoint(190,210));
    clip[0].push_back(IntPoint(240,210));
    clip[0].push_back(IntPoint(240,130));
    clip[0].push_back(IntPoint(190,130));

    Clipper c;
    c.AddPolygons(subj, ptSubject);
    c.AddPolygons(clip, ptClip);
    c.Execute(ctIntersection, solution, pftNonZero, pftNonZero);

#endif

}
