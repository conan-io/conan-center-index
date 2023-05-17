#include <cstdlib>
#include <iostream>

#include <cereal/archives/binary.hpp>


struct Data
{
    int x, y, z;
    template<class Archive>
    void serialize(Archive & archive) { archive( x, y, z ); }
};


int main() {
    std::cout << "Serialized data: ";
    {
        cereal::BinaryOutputArchive oarchive(std::cout);
        Data d1{42, 12, 52};
        Data d2{33, 34, 35};
        Data d3{74, 34, 45};
        oarchive(d1, d2, d3);
    }
    std::cout << std::endl;

    return EXIT_SUCCESS;
}
