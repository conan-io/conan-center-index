/*
 *  This example writes data to the HDF5 file.
 *  Number of processes is assumed to be 1 or multiples of 2 (up to 8)
 */

#include "hdf5.h"
#include "stdlib.h"

#define H5FILE_NAME     "SDS.h5"
#define DATASETNAME 	"IntArray"
#define NX     8                      /* dataset dimensions */
#define NY     5
#define RANK   2

int test_parallel(int argc, char **argv)
{
    /*
     * HDF5 APIs definitions
     */
    hid_t       file_id, dset_id;         /* file and dataset identifiers */
    hid_t       filespace;      /* file and memory dataspace identifiers */
    hsize_t     dimsf[] = {NX, NY};                 /* dataset dimensions */
    int         *data;                    /* pointer to data buffer to write */
    hid_t	plist_id;                 /* property list identifier */
    int         i;
    herr_t      status;

    /*
     * MPI variables
     */
    int mpi_size, mpi_rank;
    MPI_Comm comm  = MPI_COMM_WORLD;
    MPI_Info info  = MPI_INFO_NULL;

    /*
     * Initialize MPI
     */
    MPI_Init(&argc, &argv);
    MPI_Comm_size(comm, &mpi_size);
    MPI_Comm_rank(comm, &mpi_rank);

    /*
     * Initialize data buffer
     */
    data = (int *) malloc(sizeof(int)*dimsf[0]*dimsf[1]);
    for (i=0; i < dimsf[0]*dimsf[1]; i++) {
        data[i] = i;
    }
    /*
     * Set up file access property list with parallel I/O access
     */
     plist_id = H5Pcreate(H5P_FILE_ACCESS);
                H5Pset_fapl_mpio(plist_id, comm, info);

    /*
     * Create a new file collectively and release property list identifier.
     */
    file_id = H5Fcreate(H5FILE_NAME, H5F_ACC_TRUNC, H5P_DEFAULT, plist_id);
              H5Pclose(plist_id);


    /*
     * Create the dataspace for the dataset.
     */
    filespace = H5Screate_simple(RANK, dimsf, NULL);

    /*
     * Create the dataset with default properties and close filespace.
     */
    dset_id = H5Dcreate(file_id, DATASETNAME, H5T_NATIVE_INT, filespace,
			H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
    /*
     * Create property list for collective dataset write.
     */
    plist_id = H5Pcreate(H5P_DATASET_XFER);
               H5Pset_dxpl_mpio(plist_id, H5FD_MPIO_COLLECTIVE);

    /*
     * To write dataset independently use
     *
     * H5Pset_dxpl_mpio(plist_id, H5FD_MPIO_INDEPENDENT);
     */

    status = H5Dwrite(dset_id, H5T_NATIVE_INT, H5S_ALL, H5S_ALL,
		      plist_id, data);
    free(data);

    /*
     * Close/release resources.
     */
    H5Dclose(dset_id);
    H5Sclose(filespace);
    H5Pclose(plist_id);
    H5Fclose(file_id);

    MPI_Finalize();

    return 0;
}
