#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
 
 
int main(argc,argv)
     int argc;
     char **argv;
{
  char hello[] = "Hello World!";
  char hi[] = "hi!";
 
  Display *mydisplay;
  Window  mywindow;
 
  GC      mygc;
  
  XEvent myevent;
  KeySym mykey;
  
  XSizeHints myhint;
  
  int myscreen;
  unsigned long myforeground, mybackground;
  int i;
  char text[10];
  int done;
 
  /* setup display/screen */
  mydisplay = XOpenDisplay("");
  
  myscreen = DefaultScreen(mydisplay);
 
  /* drawing contexts for an window */
  myforeground = BlackPixel(mydisplay, myscreen);
  mybackground = WhitePixel(mydisplay, myscreen);
  myhint.x = 200;
  myhint.y = 300;
  myhint.width = 350;
  myhint.height = 250;
  myhint.flags = PPosition|PSize;
 
  /* create window */
  mywindow = XCreateSimpleWindow(mydisplay, DefaultRootWindow(mydisplay),
                                 myhint.x, myhint.y,
                                 myhint.width, myhint.height,
                                 5, myforeground, mybackground);
 
  /* window manager properties (yes, use of StdProp is obsolete) */
  XSetStandardProperties(mydisplay, mywindow, hello, hello,
                         None, argv, argc, &myhint);
 
  /* graphics context */
  mygc = XCreateGC(mydisplay, mywindow, 0, 0);
  XSetBackground(mydisplay, mygc, mybackground);
  XSetForeground(mydisplay, mygc, myforeground);
 
  /* allow receiving mouse events */
  XSelectInput(mydisplay,mywindow,
               ButtonPressMask|KeyPressMask|ExposureMask);
 
  /* show up window */
  XMapRaised(mydisplay, mywindow);
 
  /* event loop */
  done = 0;
  while(done==0){
 
    /* fetch event */
    XNextEvent(mydisplay, &myevent);
 
    switch(myevent.type){
      
    case Expose:
      /* Window was showed. */
      if(myevent.xexpose.count==0)
        XDrawImageString(myevent.xexpose.display,
                         myevent.xexpose.window,
                         mygc, 
                         50, 50, 
                         hello, strlen(hello));
      break;
    case MappingNotify:
      /* Modifier key was up/down. */
      XRefreshKeyboardMapping(&myevent);
      break;
    case ButtonPress:
      /* Mouse button was pressed. */
      XDrawImageString(myevent.xbutton.display,
                       myevent.xbutton.window,
                       mygc, 
                       myevent.xbutton.x, myevent.xbutton.y,
                       hi, strlen(hi));
      break;
    case KeyPress:
      /* Key input. */
      i = XLookupString(&myevent, text, 10, &mykey, 0);
      if(i==1 && text[0]=='q') done = 1;
      break;
    }
  }
  
  /* finalization */
  XFreeGC(mydisplay,mygc);
  XDestroyWindow(mydisplay, mywindow);
  XCloseDisplay(mydisplay);
 
  exit(0);
}