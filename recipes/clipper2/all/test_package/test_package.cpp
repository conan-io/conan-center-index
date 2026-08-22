#include <cstdlib>
#include <string>

#include "clipper2/clipper.h"

using namespace Clipper2Lib;

void DoSimpleTest(bool show_solution_coords = false);
Path64 MakeRandomPoly(int width, int height, unsigned vertCnt);

int main()
{
  DoSimpleTest();
}

inline Path64 MakeStar(const Point64& center, int radius, int points)
{
  if (!(points % 2)) --points;
  if (points < 5) points = 5;
  Path64 tmp = Ellipse<int64_t>(center, radius, radius, points);
  Path64 result;
  result.reserve(points);
  result.push_back(tmp[0]);
  for (int i = points - 1, j = i / 2; j;)
  {
    result.push_back(tmp[j--]);
    result.push_back(tmp[i--]);
  }
  return result;
}

void DoSimpleTest(bool show_solution_coords)
{
  Paths64 tmp, solution;
  FillRule fr = FillRule::NonZero;

  Paths64 subject, clip;
  subject.push_back(MakeStar(Point64(225, 225), 220, 9));
  clip.push_back(Ellipse<int64_t>(Point64(225,225), 150, 150));

  //Intersect both shapes and then 'inflate' result -10 (ie deflate)
  solution = Intersect(subject, clip, fr);
  solution = InflatePaths(solution, -10, JoinType::Round, EndType::Polygon);
}

