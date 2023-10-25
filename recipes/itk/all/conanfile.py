from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import glob
import os
import textwrap

required_conan_version = ">=1.53.0"


class ITKConan(ConanFile):
    name = "itk"
    description = "Open-source, cross-platform toolkit for N-dimensional scientific image processing, segmentation, and registration"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.itk.org/"
    topics = ("medical-imaging", "scientific", "image", "processing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "4.8.1",
            "clang": "3.3",
            "apple-clang": "9",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # TODO: Some packages can be added as optional, but they are not in CCI:
        # - mkl
        # - vtk
        # - opencv
        #todo: enable after fixing dcmtk compatibility with openssl on Windows
        #self.requires("dcmtk/3.6.7")
        self.requires("double-conversion/3.3.0")
        self.requires("eigen/3.4.0")
        self.requires("expat/2.5.0")
        self.requires("fftw/3.3.10")
        self.requires("gdcm/3.0.21")
        self.requires("hdf5/1.14.1")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        self.requires("libtiff/4.5.1")
        self.requires("openjpeg/2.5.0")
        self.requires("onetbb/2021.9.0")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.options.shared and not self.dependencies["hdf5"].options.shared:
            raise ConanInvalidConfiguration("When building a shared itk, hdf5 needs to be shared too (or not linked to by the consumer).\n"
                                            "This is because H5::DataSpace::ALL might get initialized twice, which will cause a H5::DataSpaceIException to be thrown).")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 190)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        #call find_package on top level
        tc.cache_variables["CMAKE_PROJECT_ITK_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["ITK_SKIP_PATH_LENGTH_CHECKS"] = True

        tc.variables["ITK_USE_SYSTEM_LIBRARIES"] = True
        tc.variables["ITK_USE_SYSTEM_DCMTK"] = True
        tc.variables["ITK_USE_SYSTEM_DOUBLECONVERSION"] = True
        tc.variables["ITK_USE_SYSTEM_EIGEN"] = True
        tc.variables["ITK_USE_SYSTEM_FFTW"] = True
        tc.variables["ITK_USE_SYSTEM_GDCM"] = True
        tc.variables["ITK_USE_SYSTEM_HDF5"] = True
        tc.variables["ITK_USE_SYSTEM_ICU"] = True
        tc.variables["ITK_USE_SYSTEM_JPEG"] = True
        tc.variables["ITK_USE_SYSTEM_PNG"] = True
        tc.variables["ITK_USE_SYSTEM_TIFF"] = True
        tc.variables["ITK_USE_SYSTEM_ZLIB"] = True

        # FIXME: Missing Kwiml recipe
        tc.variables["ITK_USE_SYSTEM_KWIML"] = False
        # FIXME: Missing VXL recipe
        tc.variables["ITK_USE_SYSTEM_VXL"] = False
        tc.variables["GDCM_USE_SYSTEM_OPENJPEG"] = True

        tc.variables["ITK_BUILD_DEFAULT_MODULES"] = False
        tc.variables["Module_ITKDeprecated"] = False
        tc.variables["Module_ITKMINC"] = False
        tc.variables["Module_ITKIOMINC"] = False

        tc.variables["Module_ITKVideoBridgeOpenCV"] = False

        #todo: enable after fixing dcmtk compatibility with openssl on Windows
        tc.variables["Module_ITKDCMTK"] = False
        tc.variables["Module_ITKIODCMTK"] = False

        tc.variables["Module_ITKIOHDF5"] = True
        tc.variables["Module_ITKIOTransformHDF5"] = False
        tc.variables["Module_ITKAnisotropicSmoothing"] = True
        tc.variables["Module_ITKAntiAlias"] = True
        tc.variables["Module_ITKBiasCorrection"] = True
        tc.variables["Module_ITKBinaryMathematicalMorphology"] = True
        tc.variables["Module_ITKBioCell"] = True
        tc.variables["Module_ITKClassifiers"] = True
        tc.variables["Module_ITKColormap"] = True
        tc.variables["Module_ITKConnectedComponents"] = True
        tc.variables["Module_ITKConvolution"] = True
        tc.variables["Module_ITKCurvatureFlow"] = True
        tc.variables["Module_ITKDeconvolution"] = True
        tc.variables["Module_ITKDeformableMesh"] = True
        tc.variables["Module_ITKDenoising"] = True
        tc.variables["Module_ITKDiffusionTensorImage"] = True
        tc.variables["Module_ITKDisplacementField"] = True
        tc.variables["Module_ITKDistanceMap"] = True
        tc.variables["Module_ITKEigen"] = True
        tc.variables["Module_ITKFEM"] = True
        tc.variables["Module_ITKFEMRegistration"] = True
        tc.variables["Module_ITKFFT"] = True
        tc.variables["Module_ITKFastMarching"] = True
        tc.variables["Module_ITKGIFTI"] = True
        tc.variables["Module_ITKGPUAnisotropicSmoothing"] = True
        tc.variables["Module_ITKGPUImageFilterBase"] = True
        tc.variables["Module_ITKGPUPDEDeformableRegistration"] = True
        tc.variables["Module_ITKGPURegistrationCommon"] = True
        tc.variables["Module_ITKGPUSmoothing"] = True
        tc.variables["Module_ITKGPUThresholding"] = True
        tc.variables["Module_ITKIOCSV"] = True
        tc.variables["Module_ITKIOGE"] = True
        tc.variables["Module_ITKIOIPL"] = True
        tc.variables["Module_ITKIOMesh"] = True
        tc.variables["Module_ITKIOPhilipsREC"] = True
        tc.variables["Module_ITKIORAW"] = True
        tc.variables["Module_ITKIOSiemens"] = True
        tc.variables["Module_ITKIOSpatialObjects"] = True
        tc.variables["Module_ITKIOTransformBase"] = True
        tc.variables["Module_ITKIOTransformInsightLegacy"] = True
        tc.variables["Module_ITKIOTransformMatlab"] = True
        tc.variables["Module_ITKIOXML"] = True
        tc.variables["Module_ITKImageCompare"] = True
        tc.variables["Module_ITKImageCompose"] = True
        tc.variables["Module_ITKImageFeature"] = True
        tc.variables["Module_ITKImageFusion"] = True
        tc.variables["Module_ITKImageGradient"] = True
        tc.variables["Module_ITKImageGrid"] = True
        tc.variables["Module_ITKImageIntensity"] = True
        tc.variables["Module_ITKImageLabel"] = True
        tc.variables["Module_ITKImageSources"] = True
        tc.variables["Module_ITKImageStatistics"] = True
        tc.variables["Module_ITKIntegratedTest"] = True
        tc.variables["Module_ITKKLMRegionGrowing"] = True
        tc.variables["Module_ITKLabelMap"] = True
        tc.variables["Module_ITKLabelVoting"] = True
        tc.variables["Module_ITKLevelSets"] = True
        tc.variables["Module_ITKLevelSetsv4"] = True
        tc.variables["Module_ITKMarkovRandomFieldsClassifiers"] = True
        tc.variables["Module_ITKMathematicalMorphology"] = True
        tc.variables["Module_ITKMetricsv4"] = True
        tc.variables["Module_ITKNarrowBand"] = True
        tc.variables["Module_ITKNeuralNetworks"] = True
        tc.variables["Module_ITKOptimizers"] = True
        tc.variables["Module_ITKOptimizersv4"] = True
        tc.variables["Module_ITKPDEDeformableRegistration"] = True
        tc.variables["Module_ITKPath"] = True
        tc.variables["Module_ITKPolynomials"] = True
        tc.variables["Module_ITKQuadEdgeMeshFiltering"] = True
        tc.variables["Module_ITKRegionGrowing"] = True
        tc.variables["Module_ITKRegistrationCommon"] = True
        tc.variables["Module_ITKRegistrationMethodsv4"] = True
        tc.variables["Module_ITKReview"] = True
        tc.variables["Module_ITKSignedDistanceFunction"] = True
        tc.variables["Module_ITKSmoothing"] = True
        tc.variables["Module_ITKSpatialFunction"] = True
        tc.variables["Module_ITKTBB"] = True
        tc.variables["Module_ITKThresholding"] = True
        tc.variables["Module_ITKVideoCore"] = True
        tc.variables["Module_ITKVideoFiltering"] = True
        tc.variables["Module_ITKVideoIO"] = False
        tc.variables["Module_ITKVoronoi"] = True
        tc.variables["Module_ITKWatersheds"] = True
        tc.variables["Module_ITKDICOMParser"] = True

        tc.variables["Module_ITKVTK"] = False
        tc.variables["Module_ITKVtkGlue"] = False

        # Disabled on Linux (link errors)
        tc.variables["Module_ITKLevelSetsv4Visualization"] = False

        # Disabled because Vxl vidl is not built anymore
        tc.variables["Module_ITKVideoBridgeVXL"] = False

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        #The CMake policy CMP0091 must be NEW, but is ''
        replace_in_file(self,
                        os.path.join(self.source_folder, "Modules", "ThirdParty", "VNL", "src", "vxl", "config", "cmake", "config", "VXLIntrospectionConfig.cmake"),
                        "-DCMAKE_CXX_FLAGS:STRING=${CMAKE_CXX_FLAGS}",
                        "-DCMAKE_POLICY_DEFAULT_CMP0091=NEW -DCMAKE_CXX_FLAGS:STRING=${CMAKE_CXX_FLAGS}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _itk_subdir(self):
        v = Version(self.version)
        return f"ITK-{v.major}.{v.minor}"

    @property
    def _cmake_module_dir(self):
        return os.path.join("lib", "cmake", self._itk_subdir)

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._cmake_module_dir, f"conan-official-{self.name}-targets.cmake")

    @property
    def _itk_components(self):
        def libm():
            return ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []
        def libdl():
            return ["dl"] if self.settings.os in ["Linux", "FreeBSD"] else []

        return {
            "itksys": {"system_libs": libdl()},
            "itkvcl": {"system_libs": libm()},
            "itkv3p_netlib": {"system_libs": libm()},
            "itkvnl": {"requires": ["itkvcl"]},
            "itkvnl_algo": {"requires": ["itkv3p_netlib", "itkvnl"]},
            "itktestlib": {"requires": ["itkvcl"]},
            "ITKVNLInstantiation": {
                "requires": [
                    "itkvnl_algo", "itkvnl", "itkv3p_netlib", "itkvcl",
                ],
            },
            "ITKCommon": {
                "requires": [
                    "itksys", "ITKVNLInstantiation", "eigen::eigen",
                    "onetbb::onetbb", "double-conversion::double-conversion",
                ],
                "system_libs": libm(),
            },
            "itkNetlibSlatec": {"requires": ["itkv3p_netlib"]},
            "ITKStatistics": {"requires": ["ITKCommon", "itkNetlibSlatec"]},
            "ITKTransform": {"requires": ["ITKCommon"]},
            "ITKMesh": {"requires": ["ITKTransform"]},
            "ITKMetaIO": {"requires": ["zlib::zlib"]},
            "ITKSpatialObjects": {"requires": ["ITKTransform", "ITKCommon", "ITKMesh"]},
            "ITKPath": {"requires": ["ITKCommon"]},
            "ITKImageIntensity": {},
            "ITKLabelMap": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                ],
            },
            "ITKQuadEdgeMesh": {"requires": ["ITKMesh"]},
            "ITKFastMarching": {},
            "ITKIOImageBase": {"requires": ["ITKCommon"]},
            "ITKSmoothing": {},
            "ITKImageFeature": {"requires": ["ITKSmoothing", "ITKSpatialObjects"]},
            "ITKOptimizers": {"requires": ["ITKStatistics"]},
            "ITKPolynomials": {"requires": ["ITKCommon"]},
            "ITKBiasCorrection": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                ],
            },
            "ITKColormap": {},
            "ITKFFT": {"requires": ["ITKCommon", "fftw::fftw"]},
            "ITKConvolution": {
                "requires": [
                    "ITKFFT", "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                ],
            },
            "ITKDICOMParser": {},
            "ITKDeformableMesh": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform", "ITKImageFeature",
                    "ITKSpatialObjects", "ITKPath", "ITKMesh",
                ],
            },
            "ITKDenoising": {},
            "ITKDiffusionTensorImage": {},
            "ITKIOXML": {"requires": ["ITKIOImageBase", "expat::expat"]},
            "ITKIOSpatialObjects": {"requires": ["ITKSpatialObjects", "ITKIOXML", "ITKMesh"]},
            "ITKFEM": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                    "ITKSmoothing", "ITKImageFeature", "ITKOptimizers", "ITKMetaIO",
                ],
            },
            "ITKPDEDeformableRegistration": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath", "ITKSmoothing",
                    "ITKImageFeature", "ITKOptimizers",
                ],
            },
            "ITKFEMRegistration": {
                "requires": [
                    "ITKFEM", "ITKImageFeature", "ITKCommon", "ITKSpatialObjects",
                    "ITKTransform", "ITKPDEDeformableRegistration",
                ],
            },
            "ITKznz": {"requires": ["zlib::zlib"]},
            "ITKniftiio": {"requires": ["ITKznz"], "system_libs": libm()},
            "ITKgiftiio": {"requires": ["ITKznz", "ITKniftiio", "expat::expat"]},
            "ITKIOBMP": {"requires": ["ITKIOImageBase"]},
            "ITKIOBioRad": {"requires": ["ITKIOImageBase"]},
            "ITKIOCSV": {"requires": ["ITKIOImageBase"]},
            #todo: enable after fixing dcmtk compatibility with openssl on Windows
            #"ITKIODCMTK": {"requires": ["ITKIOImageBase", "dcmtk::dcmtk"]},
            "ITKIOGDCM": {"requires": ["ITKCommon", "ITKIOImageBase", "gdcm::gdcmDICT", "gdcm::gdcmMSFF"]},
            "ITKIOIPL": {"requires": ["ITKIOImageBase"]},
            "ITKIOGE": {"requires": ["ITKIOIPL", "ITKIOImageBase"]},
            "ITKIOGIPL": {"requires": ["ITKIOImageBase", "zlib::zlib"]},
            "ITKIOHDF5": {"requires": ["ITKIOImageBase", "hdf5::hdf5"]},
            "ITKIOJPEG": {"requires": ["ITKIOImageBase", "libjpeg::libjpeg"]},
            "ITKIOMeshBase": {
                "requires": [
                    "ITKCommon", "ITKIOImageBase", "ITKMesh", "ITKQuadEdgeMesh",
                ],
            },
            "ITKIOMeshBYU": {"requires": ["ITKCommon", "ITKIOMeshBase"]},
            "ITKIOMeshFreeSurfer": {"requires": ["ITKCommon", "ITKIOMeshBase"]},
            "ITKIOMeshGifti": {"requires": ["ITKCommon", "ITKIOMeshBase", "ITKgiftiio"]},
            "ITKIOMeshOBJ": {"requires": ["ITKCommon", "ITKIOMeshBase"]},
            "ITKIOMeshOFF": {"requires": ["ITKCommon", "ITKIOMeshBase"]},
            "ITKIOMeshVTK": {"requires": ["ITKCommon", "ITKIOMeshBase", "double-conversion::double-conversion"]},
            "ITKIOMeta": {"requires": ["ITKIOImageBase", "ITKMetaIO"]},
            "ITKIONIFTI": {"requires": ["ITKIOImageBase", "ITKznz", "ITKniftiio", "ITKTransform"]},
            "ITKNrrdIO": {"requires": ["zlib::zlib"]},
            "ITKIONRRD": {"requires": ["ITKIOImageBase", "ITKNrrdIO"]},
            "ITKIOPNG": {"requires": ["ITKIOImageBase", "libpng::libpng"]},
            "ITKIOPhilipsREC": {"requires": ["zlib::zlib"]},
            "ITKIOSiemens": {"requires": ["ITKIOImageBase", "ITKIOIPL"]},
            "ITKIOStimulate": {"requires": ["ITKIOImageBase"]},
            "ITKIOTIFF": {"requires": ["ITKIOImageBase", "libtiff::libtiff"]},
            "ITKTransformFactory": {"requires": ["ITKCommon", "ITKTransform"]},
            "ITKIOTransformBase": {"requires": ["ITKCommon", "ITKTransform", "ITKTransformFactory"]},
            "ITKIOTransformHDF5": {"requires": ["ITKIOTransformBase", "hdf5::hdf5"]},
            "ITKIOTransformInsightLegacy": {"requires": ["ITKIOTransformBase", "double-conversion::double-conversion"]},
            "ITKIOTransformMatlab": {"requires": ["ITKIOTransformBase"]},
            "ITKIOVTK": {"requires": ["ITKIOImageBase"]},
            "ITKKLMRegionGrowing": {"requires": ["ITKCommon"]},
            "itklbfgs": {},
            "ITKMarkovRandomFieldsClassifiers": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                ],
            },
            "ITKOptimizersv4": {"requires": ["ITKOptimizers", "itklbfgs"]},
            "itkopenjpeg": {"header_only": True, "requires": ["openjpeg::openjpeg"]},
            "ITKQuadEdgeMeshFiltering": {"requires": ["ITKMesh"]},
            "ITKRegionGrowing": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath",
                ],
            },
            "ITKRegistrationMethodsv4": {
                "requires": [
                    "ITKCommon", "ITKOptimizersv4", "ITKStatistics", "ITKTransform",
                    "ITKSpatialObjects", "ITKPath", "ITKSmoothing", "ITKImageFeature",
                    "ITKOptimizers",
                ],
            },
            "ITKVTK": {"requires": ["ITKCommon"]},
            "ITKWatersheds": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform", "ITKSpatialObjects",
                    "ITKPath", "ITKSmoothing",
                ],
            },
            "ITKReview": {
                "requires": [
                    "ITKCommon", "ITKStatistics", "ITKTransform", "ITKLabelMap",
                    "ITKSpatialObjects", "ITKPath", "ITKFastMarching", "ITKIOImageBase",
                    "ITKImageFeature", "ITKOptimizers", "ITKBiasCorrection",
                    "ITKDeformableMesh", "ITKDiffusionTensorImage", "ITKSmoothing",
                    "ITKFFT", "ITKIOBMP", "ITKIOBioRad", "ITKIOGDCM", "ITKIOGE",
                    "ITKIOGIPL", "ITKIOIPL", "ITKIOJPEG", "ITKIOMeta", "ITKIONIFTI",
                    "ITKIONRRD", "ITKIOPNG", "ITKIOSiemens", "ITKIOStimulate", "ITKIOTIFF",
                    "ITKIOTransformHDF5", "ITKIOTransformInsightLegacy",
                    "ITKIOTransformMatlab", "ITKIOVTK", "ITKIOXML", "ITKKLMRegionGrowing",
                    "ITKMarkovRandomFieldsClassifiers", "ITKMesh", "ITKPDEDeformableRegistration",
                    "ITKPolynomials", "ITKQuadEdgeMesh", "ITKQuadEdgeMeshFiltering",
                    "ITKRegionGrowing", "ITKVTK", "ITKWatersheds", "itkopenjpeg",
                ],
            },
            "ITKTestKernel": {
                "requires": [
                    "ITKCommon", "ITKIOImageBase", "ITKIOBMP", "ITKIOGDCM", "ITKIOGIPL",
                    "ITKIOJPEG", "ITKIOMeshBYU", "ITKIOMeshFreeSurfer", "ITKIOMeshGifti",
                    "ITKIOMeshOBJ", "ITKIOMeshOFF", "ITKIOMeshVTK", "ITKIOMeta", "ITKIONIFTI",
                    "ITKIONRRD", "ITKIOPNG", "ITKIOTIFF", "ITKIOVTK",
                ],
            },
            "ITKVideoCore": {"requires": ["ITKCommon"]},
        }

    def _create_cmake_module_alias_targets(self):
        targets = {target:f"ITK::{target}" for target in self._itk_components.keys()}
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, os.path.join(self.package_folder, self._module_file_rel_path), content)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, self._cmake_module_dir, "Modules"))
        # Do not remove UseITK.cmake and *.h.in files
        for cmake_file in glob.glob(os.path.join(self.package_folder, self._cmake_module_dir, "*.cmake")):
            if os.path.basename(cmake_file) != "UseITK.cmake":
                os.remove(cmake_file)
        self._create_cmake_module_alias_targets()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ITK")
        self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._cmake_module_dir, "UseITK.cmake")])

        itk_version = Version(self.version)
        lib_suffix = f"-{itk_version.major}.{itk_version.minor}"

        for name, values in self._itk_components.items():
            is_header_only = values.get("header_only", False)
            system_libs = values.get("system_libs", [])
            requires = values.get("requires", [])
            self.cpp_info.components[name].set_property("cmake_target_name", name)
            self.cpp_info.components[name].set_property("cmake_target_aliases", [f"ITK::{name}"])
            self.cpp_info.components[name].builddirs.append(self._cmake_module_dir)
            self.cpp_info.components[name].includedirs.append(os.path.join("include", self._itk_subdir))
            if not is_header_only:
                self.cpp_info.components[name].libs = [f"{name}{lib_suffix}"]
            self.cpp_info.components[name].system_libs = system_libs
            self.cpp_info.components[name].requires = requires

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            for generator in ["cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.components[name].names[generator] = name
                self.cpp_info.components[name].build_modules[generator].append(self._module_file_rel_path)
                self.cpp_info.components[name].build_modules[generator].append(os.path.join(self._cmake_module_dir, "UseITK.cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.names[generator] = "ITK"
