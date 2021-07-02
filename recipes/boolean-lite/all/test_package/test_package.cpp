#include "nonstd/boolean.hpp"
#include <iostream>

using nonstd::boolean_;

void eat_cookies( int count, boolean_ leave_crumbs )
{
    std::cout << "Eat " << count << " cookies and leave " << (leave_crumbs ? "" : "no ") << "crumbs\n";
}

void santa( int num_cookies )
{
    const boolean_ leave_crumbs( num_cookies > 4 );

//  eat_cookies( leave_crumbs, num_cookies );  // Does not compile: wrong argument order
    eat_cookies( num_cookies, leave_crumbs );  // Ok
}

int main()
{
    santa( 3 );
    santa( 5 );
}
