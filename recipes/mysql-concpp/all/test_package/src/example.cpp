#include <mysqlx/xdevapi.h>
#include <iostream>

using ::std::cout;
using ::std::endl;
using namespace ::mysqlx;

int main(int argc, const char *argv[])
{
    try
    {
        const char *url = (argc > 1 ? argv[1] : "mysqlx://root:password@127.0.0.1");

        cout << "Creating session on " << url
             << " ..." << endl;

        Session sess(url);
        cout << "Session accepted." << endl;
    }
    catch (const mysqlx::Error &err)
    {
        cout << "ERROR: " << err << endl;
    }
    catch (std::exception &ex)
    {
        cout << "STD EXCEPTION: " << ex.what() << endl;
    }
    catch (const char *ex)
    {
        cout << "EXCEPTION: " << ex << endl;
    }

    cout << "Test ended." << endl;

    return 0;
}