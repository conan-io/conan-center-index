#include <X11/Xlib.h>
#include <X11/Xutil.h>

int main()
{
  Display *mydisplay;
  mydisplay = XOpenDisplay("");
  XCloseDisplay(mydisplay);
  return 0;
}