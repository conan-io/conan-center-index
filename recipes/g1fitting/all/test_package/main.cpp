#include <iostream>
#include <vector>

#include "Clothoid.hh"

Clothoid::valueType test_pi = 3.14159265358979323846264338328;

int main() {
    Clothoid::ClothoidCurve c1(0,0,test_pi*0.7,-0.1,0.05,20) ;
    Clothoid::ClothoidCurve c2(-10,0,test_pi/4,0.1,-0.05,20) ;
    std::vector<Clothoid::valueType> s1, s2 ;
    Clothoid::indexType max_iter  = 10 ;
    Clothoid::valueType tolerance = 1e-8 ;
    try {
        c1.intersect( 0, c2, 0, s1, s2, max_iter, tolerance ) ;
        std::cout << "ok = TRUE" << std::endl ;
    }
    catch (...) {
        std::cout  << "ok = FALSE\n" ;
    }
    for ( long unsigned int i = 0 ; i < s1.size() ; ++i ) {
        std::cout << "S1[" << i << "] = " << s1[i] << std::endl ;
    }
    for ( long unsigned int i = 0 ; i < s2.size() ; ++i ) {
        std::cout << "S2[" << i << "] = " << s2[i] << std::endl ;
    }
    return 0 ;
}
