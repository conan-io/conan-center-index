#include <vigra/tinyvector.hxx>
#include <vigra/impex.hxx>
#include <iostream>

using std::cout;
using std::endl;

using namespace vigra;

int main()
{
    cout << "creating a fixed size vigra array.." << endl;

    vigra::TinyVector<double, 5> arr = {1.1, 2.2, 3.3, 4.4, 5.5};

    cout << "formats supported: " << endl;
    cout << impexListFormats() << endl;
}
