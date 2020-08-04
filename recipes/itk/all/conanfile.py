from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class ITKConan(ConanFile):
    name = "itk"
    topics = ("itk", "scientific", "image", "processing")
    homepage = "http://www.itk.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    description = "Insight Segmentation and Registration Toolkit"
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    # TODO: Some packages can be added as optional, but they are not in CCI:
    # - mkl
    # - fftw
    # - vtk
    # - opencv

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("itk does not support this compiler")

    def requirements(self):
        self.requires("libjpeg/9d")
        self.requires("dcmtk/3.6.5")
        self.requires("double-conversion/3.1.5")
        self.requires("eigen/3.3.7")
        self.requires("expat/2.2.9")
        self.requires("fftw/3.3.8")
        self.requires("hdf5/1.12.0")
        self.requires("icu/67.1")
        self.requires("libtiff/4.1.0")
        self.requires("libpng/1.6.37")
        self.requires("openjpeg/2.3.1")
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("InsightToolkit-{}".format(self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        self._cmake.definitions["ITK_SKIP_PATH_LENGTH_CHECKS"] = True

        self._cmake.definitions["ITK_USE_SYSTEM_LIBRARIES"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_DCMTK"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_DOUBLECONVERSION"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_EIGEN"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_FFTW"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_HDF5"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_ICU"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_JPEG"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_PNG"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_TIFF"] = True
        self._cmake.definitions["ITK_USE_SYSTEM_ZLIB"] = True

        # FIXME: Missing Kwiml recipe
        self._cmake.definitions["ITK_USE_SYSTEM_KWIML"] = False
        # FIXME: Missing VXL recipe
        self._cmake.definitions["ITK_USE_SYSTEM_VXL"] = False
        # FIXME: Missing gdcm recipe
        self._cmake.definitions["ITK_USE_SYSTEM_GDCM"] = False
        self._cmake.definitions["GDCM_USE_SYSTEM_OPENJPEG"] = True

        self._cmake.definitions["ITK_BUILD_DEFAULT_MODULES"] = False
        self._cmake.definitions["Module_ITKDeprecated"] = False
        self._cmake.definitions["Module_ITKMINC"] = False
        self._cmake.definitions["Module_ITKIOMINC"] = False
        self._cmake.definitions["Module_ITKV3Compatibility"] = False

        self._cmake.definitions["Module_ITKVideoBridgeOpenCV"] = False

        self._cmake.definitions["Module_ITKDCMTK"] = True
        self._cmake.definitions["Module_ITKIODCMTK"] = True
        self._cmake.definitions["Module_ITKIOHDF5"] = True
        self._cmake.definitions["Module_ITKIOTransformHDF5"] = False
        self._cmake.definitions["Module_ITKAnisotropicSmoothing"] = True
        self._cmake.definitions["Module_ITKAntiAlias"] = True
        self._cmake.definitions["Module_ITKBiasCorrection"] = True
        self._cmake.definitions["Module_ITKBinaryMathematicalMorphology"] = True
        self._cmake.definitions["Module_ITKBioCell"] = True
        self._cmake.definitions["Module_ITKClassifiers"] = True
        self._cmake.definitions["Module_ITKColormap"] = True
        self._cmake.definitions["Module_ITKConnectedComponents"] = True
        self._cmake.definitions["Module_ITKConvolution"] = True
        self._cmake.definitions["Module_ITKCurvatureFlow"] = True
        self._cmake.definitions["Module_ITKDeconvolution"] = True
        self._cmake.definitions["Module_ITKDeformableMesh"] = True
        self._cmake.definitions["Module_ITKDenoising"] = True
        self._cmake.definitions["Module_ITKDiffusionTensorImage"] = True
        self._cmake.definitions["Module_ITKDisplacementField"] = True
        self._cmake.definitions["Module_ITKDistanceMap"] = True
        self._cmake.definitions["Module_ITKEigen"] = True
        self._cmake.definitions["Module_ITKFEM"] = True
        self._cmake.definitions["Module_ITKFEMRegistration"] = True
        self._cmake.definitions["Module_ITKFFT"] = True
        self._cmake.definitions["Module_ITKFastMarching"] = True
        self._cmake.definitions["Module_ITKGIFTI"] = True
        self._cmake.definitions["Module_ITKGPUAnisotropicSmoothing"] = True
        self._cmake.definitions["Module_ITKGPUImageFilterBase"] = True
        self._cmake.definitions["Module_ITKGPUPDEDeformableRegistration"] = True
        self._cmake.definitions["Module_ITKGPURegistrationCommon"] = True
        self._cmake.definitions["Module_ITKGPUSmoothing"] = True
        self._cmake.definitions["Module_ITKGPUThresholding"] = True
        self._cmake.definitions["Module_ITKIOCSV"] = True
        self._cmake.definitions["Module_ITKIOGE"] = True
        self._cmake.definitions["Module_ITKIOIPL"] = True
        self._cmake.definitions["Module_ITKIOMesh"] = True
        self._cmake.definitions["Module_ITKIOPhilipsREC"] = True
        self._cmake.definitions["Module_ITKIORAW"] = True
        self._cmake.definitions["Module_ITKIOSiemens"] = True
        self._cmake.definitions["Module_ITKIOSpatialObjects"] = True
        self._cmake.definitions["Module_ITKIOTransformBase"] = True
        self._cmake.definitions["Module_ITKIOTransformInsightLegacy"] = True
        self._cmake.definitions["Module_ITKIOTransformMatlab"] = True
        self._cmake.definitions["Module_ITKIOXML"] = True
        self._cmake.definitions["Module_ITKImageCompare"] = True
        self._cmake.definitions["Module_ITKImageCompose"] = True
        self._cmake.definitions["Module_ITKImageFeature"] = True
        self._cmake.definitions["Module_ITKImageFusion"] = True
        self._cmake.definitions["Module_ITKImageGradient"] = True
        self._cmake.definitions["Module_ITKImageGrid"] = True
        self._cmake.definitions["Module_ITKImageIntensity"] = True
        self._cmake.definitions["Module_ITKImageLabel"] = True
        self._cmake.definitions["Module_ITKImageSources"] = True
        self._cmake.definitions["Module_ITKImageStatistics"] = True
        self._cmake.definitions["Module_ITKIntegratedTest"] = True
        self._cmake.definitions["Module_ITKKLMRegionGrowing"] = True
        self._cmake.definitions["Module_ITKLabelMap"] = True
        self._cmake.definitions["Module_ITKLabelVoting"] = True
        self._cmake.definitions["Module_ITKLevelSets"] = True
        self._cmake.definitions["Module_ITKLevelSetsv4"] = True
        self._cmake.definitions["Module_ITKMarkovRandomFieldsClassifiers"] = True
        self._cmake.definitions["Module_ITKMathematicalMorphology"] = True
        self._cmake.definitions["Module_ITKMetricsv4"] = True
        self._cmake.definitions["Module_ITKNarrowBand"] = True
        self._cmake.definitions["Module_ITKNeuralNetworks"] = True
        self._cmake.definitions["Module_ITKOptimizers"] = True
        self._cmake.definitions["Module_ITKOptimizersv4"] = True
        self._cmake.definitions["Module_ITKPDEDeformableRegistration"] = True
        self._cmake.definitions["Module_ITKPath"] = True
        self._cmake.definitions["Module_ITKPolynomials"] = True
        self._cmake.definitions["Module_ITKQuadEdgeMeshFiltering"] = True
        self._cmake.definitions["Module_ITKRegionGrowing"] = True
        self._cmake.definitions["Module_ITKRegistrationCommon"] = True
        self._cmake.definitions["Module_ITKRegistrationMethodsv4"] = True
        self._cmake.definitions["Module_ITKReview"] = True
        self._cmake.definitions["Module_ITKSignedDistanceFunction"] = True
        self._cmake.definitions["Module_ITKSmoothing"] = True
        self._cmake.definitions["Module_ITKSpatialFunction"] = True
        self._cmake.definitions["Module_ITKThresholding"] = True
        self._cmake.definitions["Module_ITKVideoCore"] = True
        self._cmake.definitions["Module_ITKVideoFiltering"] = True
        self._cmake.definitions["Module_ITKVideoIO"] = False
        self._cmake.definitions["Module_ITKVoronoi"] = True
        self._cmake.definitions["Module_ITKWatersheds"] = True
        self._cmake.definitions["Module_ITKDICOMParser"] = True

        self._cmake.definitions["Module_ITKVTK"] = False
        self._cmake.definitions["Module_ITKVtkGlue"] = False

        # Disabled on Linux (link errors)
        self._cmake.definitions["Module_ITKLevelSetsv4Visualization"] = False

        # Disabled because Vxl vidl is not built anymore
        self._cmake.definitions["Module_ITKVideoBridgeVXL"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.options.shared and not self.options["hdf5"].shared:
            raise ConanInvalidConfiguration("When building a shared itk, hdf5 needs to be shared too (or not linked to by the consumer).\n"
                                            "This is because H5::DataSpace::ALL might get initialized twice, which will cause a H5::DataSpaceIException to be thrown).")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)  # FIXME: correct order?
        v = tools.Version(self.version)
        self.cpp_info.includedirs.append(os.path.join("include", "ITK-{}.{}".format(v.major, v.minor)))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl", "rt"])

        # FIXME: use conan components
        self.cpp_info.names["cmake_find_package"] = "ITK"
        self.cpp_info.names["cmake_find_package_multi"] = "ITK"
