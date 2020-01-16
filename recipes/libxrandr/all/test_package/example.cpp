#include <X11/extensions/Xrandr.h>

int main()
{
  XRRScreenSize screen_size;
  screen_size.width = 100;
  screen_size.height = 100;
  return 0;
}