from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#


class NiftiClibConan(ConanFile):
    name = "nifti_clib"
    description = "C libraries for NIFTI support"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    topics = ("image")
    # package_type should usually be "library" (if there is shared option)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_nifti2": [True, False],
        "use_cifti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_nifti2": True,
        "use_cifti": False,  # seems to be beta?
    }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.3.1")
        if self.options.use_cifti:
            self.requires("expat/2.6.2")

    def validate(self):
        pass

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.variables["NIFTI_INSTALL_NO_DOCS"] = True
        tc.variables["USE_NIFTI2_CODE"] = self.options.use_nifti2
        tc.variables["USE_CIFTI_CODE"] = self.options.use_cifti
        if is_msvc(self):
            # don't use self.settings.compiler.runtime
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
            tc.preprocessor_definitions["_CRT_SECURE_NO_WARNINGS"] = 1
        tc.generate()
        # In case there are dependencies listed on requirements, CMakeDeps should be used
        tc = CMakeDeps(self)
        tc.generate()
        # In case there are dependencies listed on build_requirements, VirtualBuildEnv should be used
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()

        if is_msvc(self):  # patch in __declspec(dllimport) for a global variable that is used
            to_replace = "extern char const * const inam[];"
            fixed = "__declspec(dllimport) " + to_replace
            replace_in_file(self, os.path.join(self.source_folder, "nifticdf", "nifticdf.h"), to_replace, fixed, strict=True)

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nifti")
        self.cpp_info.set_property("cmake_target_name", "NIFTI::NIFTI")
        self.cpp_info.set_property("pkg_config_name", "nifti")
        self.cpp_info.includedirs += [ os.path.join("include", "nifti") ]

        self.cpp_info.required_components = ["ZLIB::ZLIB"]

        self.cpp_info.components["znz"].libs = ["znz"]
        self.cpp_info.components["znz"].set_property("pkg_config_name", "znz")
        self.cpp_info.components["znz"].set_property("cmake_target_name", "NIFTI::znz")
        self.cpp_info.components["znz"].includedirs += [os.path.join("include", "nifti")]

        # inside the niftilib folder
        self.cpp_info.components["niftiio"].libs = ["niftiio"]
        self.cpp_info.components["niftiio"].set_property("pkg_config_name", "niftiio")
        self.cpp_info.components["niftiio"].set_property("cmake_target_name", "NIFTI::niftiio")
        self.cpp_info.components["niftiio"].includedirs += [os.path.join("include", "nifti")]

        self.cpp_info.components["nifticdf"].libs = ["nifticdf"]
        self.cpp_info.components["nifticdf"].requires = ["niftiio"]
        self.cpp_info.components["nifticdf"].set_property("pkg_config_name", "nifticdf")
        self.cpp_info.components["nifticdf"].set_property("cmake_target_name", "NIFTI::nifticdf")
        self.cpp_info.components["nifticdf"].includedirs += [os.path.join("include", "nifti")]

        if self.options.use_nifti2:
            self.cpp_info.components["nifti2"].libs = ["nifti2"]
            self.cpp_info.components["nifti2"].requires = ["znz"]
            self.cpp_info.components["nifti2"].set_property("pkg_config_name", "nifti2")
            self.cpp_info.components["nifti2"].set_property("cmake_target_name", "NIFTI::nifti2")
            self.cpp_info.components["nifti2"].includedirs += [os.path.join("include", "nifti")]

        if self.options.use_cifti:
            self.cpp_info.components["cifti"].libs = ["cifti"]
            self.cpp_info.components["cifti"].requires = ["nifti2"]
            self.cpp_info.components["cifti"].set_property("pkg_config_name", "cifti")
            self.cpp_info.components["cifti"].set_property("cmake_target_name", "NIFTI::cifti")
            self.cpp_info.components["cifti"].includedirs += [os.path.join("include", "nifti")]

        # if self.settings.os in ["Linux", "FreeBSD"]:
        #     self.cpp_info.system_libs.append("m")
        #     self.cpp_info.system_libs.append("pthread")
        #     self.cpp_info.system_libs.append("dl")
