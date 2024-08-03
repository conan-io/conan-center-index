
#include "calc.nsmap"      // XML namespace mapping table (only needed once at the global level)
#include "soapcalcProxy.h" // the proxy class, also #includes "soapH.h" and "soapStub.h"
#include <iostream>

int main()
{
    calcProxy calc;
    calc.destroy(); // same as: soap_destroy(calc.soap); soap_end(calc.soap);
    std::cout << "gSoap Test package successful\n";
    return 0;
}
