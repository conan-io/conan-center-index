program main
    use hdf5
    implicit none

    integer :: error

    ! Initialize HDF5 library (Required in Fortran)
    call h5open_f(error)

    print *, "Testing Fortran API"
    call test_f_api()

    ! In a real scenario, you'd handle C++ or Parallel tests
    ! via conditional compilation or separate module calls.

    ! Close HDF5 library
    call h5close_f(error)

contains

    subroutine test_f_api()
        use hdf5
        implicit none

        character(len=7), parameter :: filename = "dset.h5"
        integer(hid_t)   :: file_id, dataset_id, dataspace_id
        integer(hsize_t) :: dims(2)
        integer          :: status

        ! Create a new file using default properties
        call h5fcreate_f(filename, H5F_ACC_TRUNC_F, file_id, status)

        ! Create the data space for the dataset
        dims(1) = 4
        dims(2) = 6
        call h5screate_simple_f(2, dims, dataspace_id, status)

        ! Create the dataset
        ! Note: H5T_NATIVE_INTEGER is often used for portability,
        ! but here we match your Big Endian 32-bit spec.
        call h5dcreate_f(file_id, "/dset", H5T_STD_I32BE, dataspace_id, &
                         dataset_id, status)

        ! End access to the dataset
        call h5dclose_f(dataset_id, status)

        ! Terminate access to the data space
        call h5sclose_f(dataspace_id, status)

        ! Close the file
        call h5fclose_f(file_id, status)

        if (status == 0) then
            print *, "File and dataset created successfully."
        end if
    end subroutine test_f_api

end program main
