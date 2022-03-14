#include <iostream>
#include <ignition/math/Angle.hh>

void run_angle_example()
{

    std::cout << "\n=======================================\n"
              << "\trunning angle example\n"
              << "=======================================\n";
    //! [Create an angle]
    ignition::math::Angle a;
    //! [Create an angle]
    
    // A default constructed angle should be zero.
    std::cout << "The angle 'a' should be zero: " << a << std::endl;
    //! [constant pi]
        a = ignition::math::Angle::HalfPi;
        a = ignition::math::Angle::Pi;
    //! [constant pi]
    
    //! [Output the angle in radians and degrees.]
    std::cout << "Pi in radians: " << a << std::endl;
    std::cout << "Pi in degrees: " << a.Degree() << std::endl;
    //! [Output the angle in radians and degrees.]
    
    //! [The Angle class overloads the +=, and many other, math operators.]
    a += ignition::math::Angle::HalfPi;
    //! [The Angle class overloads the +=, and many other, math operators.]
    std::cout << "Pi + PI/2 in radians: " << a << std::endl;
    //! [normalized]
    std::cout << "Normalized to the range -Pi and Pi: "
                << a.Normalized() << std::endl;
    //! [normalized]

}