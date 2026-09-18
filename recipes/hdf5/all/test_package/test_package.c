#include "hdf5.h"
#include <stdio.h>
#include <stdlib.h>
#define FILE "dset.h5"
#define FILE_COMPRESSED "dset_compressed.h5"

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

#ifdef CONAN_HDF5_WITH_ZLIB
void test_zlib_compression()
{
    hid_t   file_id, dataset_id, dataspace_id, plist_id;
    hsize_t dims[2];
    int     data[4][6];
    herr_t  status;
    int     i, j;

    /* Initialize data */
    for (i = 0; i < 4; i++)
        for (j = 0; j < 6; j++)
            data[i][j] = i * 6 + j;

    /* Check if gzip filter is available */
    htri_t avail = H5Zfilter_avail(H5Z_FILTER_DEFLATE);
    if (avail <= 0) {
        printf("ERROR: gzip filter not available!\n");
        exit(1);
    }
    printf("gzip filter is available\n");

    /* Create file */
    file_id = H5Fcreate(FILE_COMPRESSED, H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);

    /* Create dataspace */
    dims[0] = 4;
    dims[1] = 6;
    dataspace_id = H5Screate_simple(2, dims, NULL);

    /* Create dataset creation property list and enable gzip compression */
    plist_id = H5Pcreate(H5P_DATASET_CREATE);

    /* Set chunk dimensions - required for compression */
    hsize_t chunk_dims[2] = {2, 3};
    status = H5Pset_chunk(plist_id, 2, chunk_dims);
    if (status < 0) {
        printf("ERROR: Failed to set chunk dimensions!\n");
        exit(1);
    }

    status = H5Pset_deflate(plist_id, 6); /* compression level 6 */
    if (status < 0) {
        printf("ERROR: Failed to set gzip compression!\n");
        exit(1);
    }

    /* Create compressed dataset */
    dataset_id = H5Dcreate2(file_id, "/compressed_dset", H5T_NATIVE_INT, dataspace_id,
                            H5P_DEFAULT, plist_id, H5P_DEFAULT);

    /* Write data */
    status = H5Dwrite(dataset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL, H5P_DEFAULT, data);
    if (status < 0) {
        printf("ERROR: Failed to write compressed data!\n");
        exit(1);
    }

    printf("Successfully wrote compressed dataset with gzip\n");

    /* Close resources */
    H5Pclose(plist_id);
    H5Dclose(dataset_id);
    H5Sclose(dataspace_id);
    H5Fclose(file_id);
}
#endif

void test_file_locking()
{
    hid_t   file_id, fapl_id;
    herr_t  status;
    bool    use_file_locking, ignore_when_disabled;
    const char *test_file = "test_file_locking.h5";

    /* Create a file access property list */
    fapl_id = H5Pcreate(H5P_FILE_ACCESS);
    if (fapl_id < 0) {
        printf("ERROR: Failed to create file access property list!\n");
        exit(1);
    }

    /* Get the current file locking settings */
    status = H5Pget_file_locking(fapl_id, &use_file_locking, &ignore_when_disabled);
    if (status < 0) {
        printf("ERROR: Failed to get file locking settings!\n");
        exit(1);
    }

#ifdef CONAN_HDF5_FILE_LOCKING_DISABLED
    /* Verify file locking is disabled when built with file_locking=False */
    if (use_file_locking) {
        printf("ERROR: File locking should be disabled but is enabled!\n");
        printf("       use_file_locking=%d, ignore_when_disabled=%d\n",
               use_file_locking, ignore_when_disabled);
        exit(1);
    }
    printf("File locking correctly disabled (use_file_locking=%d, ignore_when_disabled=%d)\n",
           use_file_locking, ignore_when_disabled);
#else
    /* Verify file locking is enabled when built with file_locking=True (default) */
    if (!use_file_locking) {
        printf("ERROR: File locking should be enabled but is disabled!\n");
        printf("       use_file_locking=%d, ignore_when_disabled=%d\n",
               use_file_locking, ignore_when_disabled);
        exit(1);
    }
    printf("File locking correctly enabled (use_file_locking=%d, ignore_when_disabled=%d)\n",
           use_file_locking, ignore_when_disabled);
#endif

    /* Test that we can create a file with the settings */
    file_id = H5Fcreate(test_file, H5F_ACC_TRUNC, H5P_DEFAULT, fapl_id);
    if (file_id < 0) {
        printf("ERROR: Failed to create file with file locking settings!\n");
        exit(1);
    }

    printf("Successfully created file with file locking settings\n");

    /* Clean up */
    H5Fclose(file_id);
    H5Pclose(fapl_id);
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
    #ifdef CONAN_HDF5_WITH_ZLIB
    printf("Testing zlib compression\n");
    test_zlib_compression();
    #endif
    printf("Testing file locking configuration\n");
    test_file_locking();

    return 0;
}
