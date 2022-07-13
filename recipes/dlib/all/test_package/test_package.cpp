#include <dlib/logger.h>
#include <dlib/misc_api.h>

// Create a logger object somewhere.  It is usually convenient to make it at the global scope
// which is what I am doing here.  The following statement creates a logger that is named example.
dlib::logger dlog("conan-test");

int main()
{
    // Every logger has a logging level (given by dlog.level()).  Each log message is tagged with a
    // level and only levels equal to or higher than dlog.level() will be printed.  By default all
    // loggers start with level() == LERROR.  In this case I'm going to set the lowest level LALL
    // which means that dlog will print all logging messages it gets.
    dlog.set_level(dlib::LALL);

    // print our first message.  It will go to cout because that is the default.
    dlog << dlib::LINFO << "This is an informational message.";

    // now print a debug message.
    int variable = 8;
    dlog << dlib::LDEBUG << "The integer variable is set to " << variable;

    // the logger can be used pretty much like any ostream object.  But you have to give a logging
    // level first.  But after that you can chain << operators like normal.

    if (variable > 4)
        dlog << dlib::LWARN << "The variable is bigger than 4!  Its value is " << variable;

    dlog << dlib::LINFO << "we are going to sleep for half a second.";
    // sleep for half a second
    dlib::sleep(500);
    dlog << dlib::LINFO << "we just woke up";

    dlog << dlib::LINFO << "program ending";
    return 0;
}
