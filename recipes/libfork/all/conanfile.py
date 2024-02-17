from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "libfork"
    # version = "2.1.1" 
    description = "A bleeding-edge, lock-free, wait-free, continuation-stealing tasking library."
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case it's not listed there, use "LicenseRef-<license-file-name>"
    license = "MPL-2.0"
    # author = "Conor Williams"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ConorWilliams/libfork"
    # Do not put "conan" nor the project name in topics. Use topics from the upstream listed on GH
    # Keep 'header-only' as topic
    topics = ("multithreading",
              "fork-join",
              "parallelism",
              "framework",
              "continuation-stealing",
              "lockfree",
              "wait-free",
              "header-only")
    package_type = "header-library"
    # Keep settings around to make cmake_layout() happy (build_type required)
    settings = "os", "arch", "compiler", "build_type"
    
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    # In case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "12.0.0",
            "clang": "10",
            "gcc": "10",
            "msvc": "19.29",
            "Visual Studio": "16.10",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/3.28.1")
        if (not self.conf.get("tools.build:skip_test", default=True, check_type=bool)):
            self.test_requires("catch2/3.5.1")
    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        # MSVC builds are currently not supported because of a bug
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("MSVC not supported due to bug")
        # Validate the minimum cpp standard supported when installing the package. For C++ projects only
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        # Download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Generate custom packageConfig files
        deps = CMakeDeps(self)
        deps.generate()
        # Generate build system
        tc = CMakeToolchain(self)
        # Set specs for CMake. E.g. we can relieve CPM from downloading
        tc.cache_variables["CPM_USE_LOCAL_PACKAGES"] = True
        if (not self.conf.get("tools.build:skip_test", default=True, check_type=bool)):
            tc.cache_variables["libfork_DEVELOPER_MODE"] = True
            tc.cache_variables["BUILD_TESTING"] = True
        tc.generate()


    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if (not self.conf.get("tools.build:skip_test", default=True, check_type=bool)):
            cmake.test()

    # Copy all files to the package folder
    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Mimic the packageConfig files written by the library
        # For header-only packages, libdirs and bindirs are not used
         # so it's necessary to set those as empty.
        self.cpp_info.includedirs = ["include/libfork-2.1.1"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "libfork")
        self.cpp_info.set_property("cmake_target_name", "libfork::libfork")
        # TODO
        # - Provide pkconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        # self.cpp_info.set_property("pkg_config_name", "libfork")

        # Add m, pthread and dl if needed in Linux/FreeBSD
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])

        # TODO
        # - Support legacy generators such as cmake_find_package
