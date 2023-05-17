#ifdef TINYSPLINE_API_0_3
# include <tinysplinecxx.h>
#else
# include <tinysplinecpp.h>
#endif

int main() {
  tinyspline::BSpline spline(6, 3, 3);

  return 0;
}
