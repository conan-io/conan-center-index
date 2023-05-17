#include "itkLightObject.h"

#include <hdf5/hdf5.h>
#include <hdf5/H5Exception.h>

#include <iostream>

class Test : public itk::LightObject {
public:
    typedef itk::SmartPointer<Test> Pointer;
    static Pointer New() { return new Test(); }
    const char *GetNameOfClass() { return "Test"; }
};

int main(int, char **) try {
    //Test::Pointer test = Test::New();
    //std::cout << test->GetNameOfClass() << std::endl;
    return 0;
} catch(const H5::DataSpaceIException &e) {
    std::cerr << "CAUGHT\n";
    e.printErrorStack();
    return 0;
}
