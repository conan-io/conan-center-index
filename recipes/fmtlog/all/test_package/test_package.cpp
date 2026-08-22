#include "fmtlog/fmtlog.h"
int main()
{
  FMTLOG(fmtlog::INF, "The answer is {}.", 42);
}
