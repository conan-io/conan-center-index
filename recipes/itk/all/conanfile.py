import os

from conans import ConanFile, CMake, tools


class LibITKConan(ConanFile):
    name = "itk"
    topics = "Image processing"
    homepage = "http://www.itk.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    description = "Insight Segmentation and Registration Toolkit"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_jpegturbo": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_jpegturbo": False}
    generators = "cmake", "cmake_find_package"
    short_paths = True
    _source_subfolder = "sf"
    _build_subfolder = "build"
    _upstream_version = ""
    _upstream_patch = ""

    # TODO: Some packages can be added as optional, but they are not in CCI:
    # - mkl
    # - fftw
    # - vtk
    # - opencv

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        version_token = self.version.split(".")
        self._upstream_version = "{0}.{1}".format(
                                        version_token[0],
                                        version_token[1])
        self._upstream_patch = version_token[2]
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):

        if(self.options["use_jpegturbo"]):
            self.requires("libjpeg-turbo/2.0.2")
        else:
            self.requires("libjpeg/9c")

        self.requires("expat/2.2.9")
        self.requires("libtiff/4.0.9")
        self.requires("libpng/1.6.37")
        self.requires("zlib/1.2.11")
        self.requires("icu/64.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ITK-{0}.{1}".format(
            self._upstream_version,
            self._upstream_patch),
            self._source_subfolder)

    def _configure_cmake(self):
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
        cmake.definitions["ITK_USE_SYSTEM_ICU"] = "ON"

        cmake.definitions["ITK_BUILD_DEFAULT_MODULES"] = "OFF"
        cmake.definitions["Module_ITKDeprecated"] = "OFF"
        cmake.definitions["Module_ITKMINC"] = "OFF"
        cmake.definitions["Module_ITKIOMINC"] = "OFF"
        cmake.definitions["Module_ITKV3Compatibility"] = "OFF"

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

        cmake.definitions["Module_ITKVTK"] = "OFF"
        cmake.definitions["Module_ITKVtkGlue"] = "OFF"

        cmake.definitions["USE_FFTWF"] = "OFF"
        cmake.definitions["USE_FFTWD"] = "OFF"

        # Disabled on Linux (link errors)
        cmake.definitions["Module_ITKLevelSetsv4Visualization"] = "OFF"

        # Disabled because Vxl vidl is not build anymore
        cmake.definitions["Module_ITKVideoBridgeVXL"] = "OFF"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.configure(build_folder=self._build_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "gdcmopenjpeg-2.1"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):

        # in linux we need to link also with these libs
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl", "rt"])

        self.cpp_info.builddirs = ['lib/cmake/ITK-{0}/'.format(
            self._upstream_version)]
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ['include']
        # This hack allow to include directly, for example, a vnl
        # file using `#include <vln/...>`
        # Without the hack, the vln files cannot themselves include
        # files using `#include<vnl/..>` since only <ITK-xx/vnl/...> is
        # available. More, one has to add in CMakeLists.txt
        # include_directories(${CONAN_INCLUDE_DIRS_ITK_SUB})
        # to finish the use of this hack.
        self.cpp_info.sub.includedirs.append('include/ITK-{0}'.format(
            self._upstream_version))
