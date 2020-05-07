#include <itkLightObject.h>

#include <iostream>

class Test : public itk::LightObject {
public:
    typedef itk::SmartPointer<Test> Pointer;
    static Pointer New() { return new Test(); }
    const char *GetNameOfClass() { return "Test"; }
};

int main(int, char **) {
    Test::Pointer test = Test::New();
    std::cout << test->GetNameOfClass() << std::endl;
}
