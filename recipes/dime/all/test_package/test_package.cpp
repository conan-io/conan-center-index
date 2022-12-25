#include <iostream>

#include <dime/Input.h>
#include <dime/Model.h>
#include <dime/State.h>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        return 1;
    }
    const char* filename = argv[1];

    dimeInput in;

    if (!in.setFile(filename)) {
        std::cerr << "could not read dxf file : " << filename << std::endl;
        return 1;
    }

    dimeModel model;
    model.read(&in);

    return 0;
}
