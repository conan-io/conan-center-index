#include <cstdlib>
#include<vector>
#include<complex>

#include"cnpy.h"

int main() {
    const int Nx = 128;
    const int Ny = 64;
    const int Nz = 32;

    std::vector<std::complex<double>> data(Nx*Ny*Nz);
    for(int i = 0;i < Nx*Ny*Nz;i++) data[i] = std::complex<double>(rand(),rand());

    cnpy::npy_save("arr1.npy",&data[0],{Nz,Ny,Nx},"w");
    cnpy::NpyArray arr = cnpy::npy_load("arr1.npy");
    std::complex<double>* loaded_data = arr.data<std::complex<double>>();

    return EXIT_SUCCESS;
}
