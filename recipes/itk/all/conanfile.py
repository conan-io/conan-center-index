import os
import re

from conans import ConanFile, CMake, tools

class LibITKConan(ConanFile):
    name = "itk"

    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_jpegturbo": [True, False],
        "use_vtk": [True, False],
        "use_fftw_float": [True, False],
        "use_fftw_double": [True, False],
        "use_opencv": [True, False],
        "use_mkl": [True, False]}

    default_options = {
        "shared": True,
        "fPIC": True,
        "use_vtk": False,
        "use_jpegturbo": False,
        "use_fftw_float": False,
        "use_fftw_double": False,
        "use_opencv": False,
        "use_mkl": False}

    homepage = "http://www.itk.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "http://www.itk.org/licensing/"
    description = "Insight Segmentation and Registration Toolkit"
    _source_subfolder = "sf"
    build_subfolder = "build"
    short_paths = True

    def configure(self):
        tools.get(**self.conan_data["sources"][self.version])
        version_token = self.version.split(".")
        self.upstream_version = "{0}.{1}".format(version_token[0], version_token[1])
        self.upstream_patch = version_token[2]
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if 'CI' not in os.environ:
            os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"

    def requirements(self):

        if(self.options["use_jpegturbo"]):
            self.requires("libjpeg-turbo/2.0.2")
        else:
            self.requires("libjpeg/9c")

        self.requires("expat/2.2.7")
        self.requires("libtiff/4.0.9")
        self.requires("libpng/1.6.37")
        self.requires("zlib/1.2.11")

        if(self.options["use_opencv"]):
            self.requires("opencv/4.1.1")

        if(self.options["use_vtk"]):
            self.options["use_vtk"] = False
            self.output.warn("VTK is not yet package in Conan center, discard dependency")
        #    self.requires("mkl/x.y.z")

        if(self.options["use_mkl"]):
            self.options["use_mkl"] = False
            self.output.warn("Intel(c)'s MKL(c) is not yet package in Conan center, discard dependency")
        #    self.requires("mkl/x.y.z")

        if(self.options["use_fftw_double"] and self.options["use_fftw_float"]):
            self.output.error("Please choose between double and float conversion for FFT library")

        if(self.options["use_fftw_double"] or self.options["use_fftw_float"]):
            self.options["use_fftw_double"] = False
            self.options["use_fftw_float"] = False
            self.output.warn("FFTW library is not yet package in Conan center, discard dependency")
        #    self.requires("fftw/x.y.z")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ITK-{0}.{1}".format(
            self.upstream_version,
            self.upstream_patch),
            self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["ITK_USE_REVIEW"] = "ON"
        cmake.definitions["ITK_SKIP_PATH_LENGTH_CHECKS"] = "ON"

        cmake.definitions["ITK_USE_SYSTEM_DCMTK"] = "OFF"
        cmake.definitions["ITK_USE_SYSTEM_GDCM"] = "OFF"
        cmake.definitions["ITK_USE_SYSTEM_PNG"] = "ON"
        cmake.definitions["ITK_USE_SYSTEM_TIFF"] = "ON"
        cmake.definitions["ITK_USE_SYSTEM_ZLIB"] = "ON"
        cmake.definitions["ITK_USE_SYSTEM_JPEG"] = "ON"
        cmake.definitions["ITK_USE_SYSTEM_EXPAT"] = "ON"

        cmake.definitions["ITK_BUILD_DEFAULT_MODULES"] = "OFF"
        cmake.definitions["Module_ITKDeprecated"] = "OFF"
        cmake.definitions["Module_ITKMINC"] = "OFF"
        cmake.definitions["Module_ITKIOMINC"] = "OFF"
        cmake.definitions["Module_ITKV3Compatibility"] = "OFF"

        if(self.options["use_opencv"]):
            cmake.definitions["Module_ITKVideoBridgeOpenCV"] = "ON"
        else:
            cmake.definitions["Module_ITKVideoBridgeOpenCV"] = "OFF"

        cmake.definitions["Module_ITKDCMTK"] = "ON"
        cmake.definitions["Module_ITKIODCMTK"] = "ON"
        cmake.definitions["Module_ITKIOHDF5"] = "ON"
        cmake.definitions["Module_ITKIOTransformHDF5"] = "OFF"
        cmake.definitions["Module_ITKAnisotropicSmoothing"] = "ON"
        cmake.definitions["Module_ITKAntiAlias"] = "ON"
        cmake.definitions["Module_ITKBiasCorrection"] = "ON"
        cmake.definitions["Module_ITKBinaryMathematicalMorphology"] = "ON"
        cmake.definitions["Module_ITKBioCell"] = "ON"
        cmake.definitions["Module_ITKClassifiers"] = "ON"
        cmake.definitions["Module_ITKColormap"] = "ON"
        cmake.definitions["Module_ITKConnectedComponents"] = "ON"
        cmake.definitions["Module_ITKConvolution"] = "ON"
        cmake.definitions["Module_ITKCurvatureFlow"] = "ON"
        cmake.definitions["Module_ITKDeconvolution"] = "ON"
        cmake.definitions["Module_ITKDeformableMesh"] = "ON"
        cmake.definitions["Module_ITKDenoising"] = "ON"
        cmake.definitions["Module_ITKDiffusionTensorImage"] = "ON"
        cmake.definitions["Module_ITKDisplacementField"] = "ON"
        cmake.definitions["Module_ITKDistanceMap"] = "ON"
        cmake.definitions["Module_ITKEigen"] = "ON"
        cmake.definitions["Module_ITKFEM"] = "ON"
        cmake.definitions["Module_ITKFEMRegistration"] = "ON"
        cmake.definitions["Module_ITKFFT"] = "ON"
        cmake.definitions["Module_ITKFastMarching"] = "ON"
        cmake.definitions["Module_ITKGIFTI"] = "ON"
        cmake.definitions["Module_ITKGPUAnisotropicSmoothing"] = "ON"
        cmake.definitions["Module_ITKGPUImageFilterBase"] = "ON"
        cmake.definitions["Module_ITKGPUPDEDeformableRegistration"] = "ON"
        cmake.definitions["Module_ITKGPURegistrationCommon"] = "ON"
        cmake.definitions["Module_ITKGPUSmoothing"] = "ON"
        cmake.definitions["Module_ITKGPUThresholding"] = "ON"
        cmake.definitions["Module_ITKIOCSV"] = "ON"
        cmake.definitions["Module_ITKIOGE"] = "ON"
        cmake.definitions["Module_ITKIOIPL"] = "ON"
        cmake.definitions["Module_ITKIOMesh"] = "ON"
        cmake.definitions["Module_ITKIOPhilipsREC"] = "ON"
        cmake.definitions["Module_ITKIORAW"] = "ON"
        cmake.definitions["Module_ITKIOSiemens"] = "ON"
        cmake.definitions["Module_ITKIOSpatialObjects"] = "ON"
        cmake.definitions["Module_ITKIOTransformBase"] = "ON"
        cmake.definitions["Module_ITKIOTransformInsightLegacy"] = "ON"
        cmake.definitions["Module_ITKIOTransformMatlab"] = "ON"
        cmake.definitions["Module_ITKIOXML"] = "ON"
        cmake.definitions["Module_ITKImageCompare"] = "ON"
        cmake.definitions["Module_ITKImageCompose"] = "ON"
        cmake.definitions["Module_ITKImageFeature"] = "ON"
        cmake.definitions["Module_ITKImageFusion"] = "ON"
        cmake.definitions["Module_ITKImageGradient"] = "ON"
        cmake.definitions["Module_ITKImageGrid"] = "ON"
        cmake.definitions["Module_ITKImageIntensity"] = "ON"
        cmake.definitions["Module_ITKImageLabel"] = "ON"
        cmake.definitions["Module_ITKImageSources"] = "ON"
        cmake.definitions["Module_ITKImageStatistics"] = "ON"
        cmake.definitions["Module_ITKIntegratedTest"] = "ON"
        cmake.definitions["Module_ITKKLMRegionGrowing"] = "ON"
        cmake.definitions["Module_ITKLabelMap"] = "ON"
        cmake.definitions["Module_ITKLabelVoting"] = "ON"
        cmake.definitions["Module_ITKLevelSets"] = "ON"
        cmake.definitions["Module_ITKLevelSetsv4"] = "ON"
        cmake.definitions["Module_ITKMarkovRandomFieldsClassifiers"] = "ON"
        cmake.definitions["Module_ITKMathematicalMorphology"] = "ON"
        cmake.definitions["Module_ITKMetricsv4"] = "ON"
        cmake.definitions["Module_ITKNarrowBand"] = "ON"
        cmake.definitions["Module_ITKNeuralNetworks"] = "ON"
        cmake.definitions["Module_ITKOptimizers"] = "ON"
        cmake.definitions["Module_ITKOptimizersv4"] = "ON"
        cmake.definitions["Module_ITKPDEDeformableRegistration"] = "ON"
        cmake.definitions["Module_ITKPath"] = "ON"
        cmake.definitions["Module_ITKPolynomials"] = "ON"
        cmake.definitions["Module_ITKQuadEdgeMeshFiltering"] = "ON"
        cmake.definitions["Module_ITKRegionGrowing"] = "ON"
        cmake.definitions["Module_ITKRegistrationCommon"] = "ON"
        cmake.definitions["Module_ITKRegistrationMethodsv4"] = "ON"
        cmake.definitions["Module_ITKReview"] = "ON"
        cmake.definitions["Module_ITKSignedDistanceFunction"] = "ON"
        cmake.definitions["Module_ITKSmoothing"] = "ON"
        cmake.definitions["Module_ITKSpatialFunction"] = "ON"
        cmake.definitions["Module_ITKThresholding"] = "ON"
        cmake.definitions["Module_ITKVideoCore"] = "ON"
        cmake.definitions["Module_ITKVideoFiltering"] = "ON"
        cmake.definitions["Module_ITKVideoIO"] = "OFF"
        cmake.definitions["Module_ITKVoronoi"] = "ON"
        cmake.definitions["Module_ITKWatersheds"] = "ON"
        cmake.definitions["Module_ITKDICOMParser"] = "ON"

        if(self.options["use_vtk"]):
            cmake.definitions["Module_ITKVTK"] = "ON"
            cmake.definitions["Module_ITKVtkGlue"] = "ON"
        else:
            cmake.definitions["Module_ITKVTK"] = "OFF"
            cmake.definitions["Module_ITKVtkGlue"] = "OFF"

        if(self.options["use_fftw_float"]):
            cmake.definitions["USE_FFTWF"] = "ON"

        if(self.options["use_fftw_double"]):
            cmake.definitions["USE_FFTWD"] = "ON"

        # Disabled on Linux (link errors)
        cmake.definitions["Module_ITKLevelSetsv4Visualization"] = "OFF"

        # Disabled because Vxl vidl is not build anymore
        cmake.definitions["Module_ITKVideoBridgeVXL"] = "OFF"

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.install()
        cmake.patch_config_paths()

    def package_info(self):
        self.cpp_info.builddirs = ['lib/cmake/ITK-{0}/'.format(
            self.upstream_version)]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']
        # This hack allow to include directly, for example, a vnl
        # file using `#include <vln/...>`
        # Without the hack, the vln files cannot themselves include
        # files using `#include<vnl/..>` since only <ITK-xx/vnl/...> is
        # available. More, one has to add in CMakeLists.txt
        # include_directories(${CONAN_INCLUDE_DIRS_ITK_SUB})
        # to finish the use of this hack.
        self.cpp_info.sub.includedirs = ['include/ITK-{0}'.format(
            self.upstream_version)]
