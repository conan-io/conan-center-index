#include <Platform.Converters.h>

#include <iostream>

using namespace Platform::Converters;

int main() {
    int source {48};
    char to = Converter<int, char>::Convert(source);
    std::cout<<"int value: "<<source<<"\nchar value: "<<to<<'\n';
    return 0;
}
