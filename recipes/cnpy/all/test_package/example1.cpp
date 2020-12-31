#include"cnpy.h"
#include<complex>
#include<cstdlib>
#include<iostream>
#include<map>
#include<string>
#include <gtest/gtest.h>

const size_t Nx = 128;
const size_t Ny = 64;
const size_t Nz = 32;

class CNPYTest : public testing::Test {
  protected:
  std::vector<std::complex<double>> data;
  void SetUp(){
    srand(0);
    data = std::vector<std::complex<double>>(Nx*Ny*Nz);
    for(int i = 0;i < Nx*Ny*Nz;i++) data[i] = std::complex<double>(rand(),rand());
  }
};

TEST_F(CNPYTest, save){
  cnpy::npy_save("arr1.npy",&data[0],{Nz,Ny,Nx},"w");
}

TEST_F(CNPYTest, load){
  cnpy::NpyArray arr = cnpy::npy_load("arr1.npy");
  std::complex<double>* loaded_data = arr.data<std::complex<double>>();
  EXPECT_EQ(arr.word_size, sizeof(std::complex<double>));
  EXPECT_EQ(arr.shape.size(), 3);
  EXPECT_EQ(arr.shape[0], Nz);
  EXPECT_EQ(arr.shape[1], Ny);
  EXPECT_EQ(arr.shape[2], Nx);
  for(int i = 0; i < Nx*Ny*Nz;i++) EXPECT_EQ(data[i],loaded_data[i]);
}

TEST_F(CNPYTest, append){
    //append the same data to file
    //npy array on file now has shape (Nz+Nz,Ny,Nx)
    cnpy::npy_save("arr1.npy",&data[0],{Nz,Ny,Nx},"a");

    //now write to an npz file
    //non-array variables are treated as 1D arrays with 1 element
    double myVar1 = 1.2;
    char myVar2 = 'a';
    cnpy::npz_save("out.npz","myVar1",&myVar1,{1},"w"); //"w" overwrites any existing file
    cnpy::npz_save("out.npz","myVar2",&myVar2,{1},"a"); //"a" appends to the file we created above
    cnpy::npz_save("out.npz","arr1",&data[0],{Nz,Ny,Nx},"a"); //"a" appends to the file we created above

    //load a single var from the npz file
    cnpy::NpyArray arr2 = cnpy::npz_load("out.npz","arr1");

    //load the entire npz file
    cnpy::npz_t my_npz = cnpy::npz_load("out.npz");
    
    //check that the loaded myVar1 matches myVar1
    cnpy::NpyArray arr_mv1 = my_npz["myVar1"];
    double* mv1 = arr_mv1.data<double>();
    EXPECT_EQ(arr_mv1.shape.size(),1);
    EXPECT_EQ(arr_mv1.shape[0], 1);
    EXPECT_EQ(mv1[0], myVar1);
}