#include <cstdlib>
#include<vector>
#include"cnpy.h"

int main() {
    const size_t Nx = 16;
    const size_t Ny = 16;
    const size_t Nz = 16;

    std::vector<double> data(Nx*Ny*Nz);
    for(int i = 0;i < Nx*Ny*Nz;i++) data[i] = rand();
    cnpy::npy_save("arr1.npy",&data[0],{Nz,Ny,Nx},"w");
    cnpy::NpyArray arr = cnpy::npy_load("arr1.npy");
    return 0;
}
