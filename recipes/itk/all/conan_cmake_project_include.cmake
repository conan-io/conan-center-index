macro(custom_find_package name)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
endmacro()

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/DCMTK/CMakeLists.txt#L99-L104
custom_find_package(DCMTK REQUIRED CONFIG)
set(ITKDCMTK_LIBRARIES dcmtk::dcmtk)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/Eigen3/CMakeLists.txt
custom_find_package(Eigen3 REQUIRED CONFIG)
set(ITKEigen3_INCLUDE_DIRS ${Eigen3_INCLUDE_DIR})
set(ITKEigen3_LIBRARIES Eigen3::Eigen)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/DoubleConversion/CMakeLists.txt
custom_find_package(double-conversion REQUIRED CONFIG)
set(ITKDoubleConversion_LIBRARIES double-conversion::double-conversion)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/Expat/CMakeLists.txt
custom_find_package(EXPAT REQUIRED CONFIG)
set(ITKExpat_LIBRARIES EXPAT::EXPAT)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/CMake/itkExternal_FFTW.cmake#L180
custom_find_package(FFTW REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/GDCM/CMakeLists.txt
custom_find_package(GDCM REQUIRED CONFIG)
set(ITKGDCM_LIBRARIES GDCM::gdcmDICT GDCM::gdcmMSFF)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/HDF5/CMakeLists.txt
custom_find_package(HDF5 REQUIRED CONFIG)
set(ITKHDF5_LIBRARIES HDF5::HDF5)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/JPEG/CMakeLists.txt
custom_find_package(JPEG REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/OpenJPEG/CMakeLists.txt
custom_find_package(OpenJPEG REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/PNG/CMakeLists.txt
custom_find_package(PNG REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/TIFF/CMakeLists.txt
custom_find_package(TIFF REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/TBB/CMakeLists.txt
custom_find_package(TBB REQUIRED CONFIG)

# https://github.com/InsightSoftwareConsortium/ITK/blob/v5.4rc01/Modules/ThirdParty/ZLIB/CMakeLists.txt
custom_find_package(ZLIB REQUIRED CONFIG)

# Prevent linking against system libraries by accident
set(CMAKE_DISABLE_FIND_PACKAGE_Perl TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_Python TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_SWIG TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_Git TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_OpenCL TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_VXL TRUE)
