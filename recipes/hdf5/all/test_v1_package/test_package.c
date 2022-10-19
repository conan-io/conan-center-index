#include "hdf5.h"
#define FILE "dset.h5"

extern void test_cxx_api();
extern void test_parallel();

void test_c_api()
{

    hid_t   file_id, dataset_id, dataspace_id; /* identifiers */
    hsize_t dims[2];
    herr_t  status;

    /* Create a new file using default properties. */
    file_id = H5Fcreate(FILE, H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);

    /* Create the data space for the dataset. */
    dims[0]      = 4;
    dims[1]      = 6;
    dataspace_id = H5Screate_simple(2, dims, NULL);

    /* Create the dataset. */
    dataset_id =
        H5Dcreate2(file_id, "/dset", H5T_STD_I32BE, dataspace_id, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /* End access to the dataset and release resources used by it. */
    status = H5Dclose(dataset_id);

    /* Terminate access to the data space. */
    status = H5Sclose(dataspace_id);

    /* Close the file. */
    status = H5Fclose(file_id);
}

int main(int argc, char **argv)
{
    printf("Testing C API\n");
    test_c_api();
    #ifdef CONAN_HDF5_CXX
    printf("Testing C++ API\n");
    test_cxx_api();
    #endif
    #ifdef CONAN_HDF5_PARALLEL
    printf("Testing HDF5 Parallel\n");
    test_parallel(argc, argv);
    #endif

    return 0;
}
