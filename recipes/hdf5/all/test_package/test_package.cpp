#include <H5Cpp.h>

extern "C" void test_cxx_api()
{
    hsize_t dimensions[] = {4, 6};
	H5::H5File file("dataset.h5", H5F_ACC_TRUNC);
	H5::DataSpace dataspace(2, dimensions);
	H5::DataSet dataset = file.createDataSet("dataset", H5::PredType::STD_I32BE, dataspace);
}
