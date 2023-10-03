import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rm, replace_in_file, save, rename
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "nanobind"
    description = "Tiny and efficient C++/Python bindings"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wjakob/nanobind"
    topics = ("python", "bindings", "pybind11")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "stable_abi": [True, False],
        "domain": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "stable_abi": False,  # FIXME: should be True by default
        "domain": None,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "192",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tsl-robin-map/1.2.1")
        # FIXME: add cpython dependency
        # self.requires("cpython/3.12.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # FIXME: need to check that we are using CPython 3.12+ for self.options.stable_abi

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NB_TEST"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    @property
    def _libname(self):
        libname = "nanobind"
        if not self.options.shared:
            libname += "-static"
        if self.options.stable_abi:
            libname += "-abi3"
        if self.options.domain and self.options.shared:
            libname += f"-{self.options.domain}"
        return libname

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._libname)

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        nb_config = os.path.join(self.source_folder, "cmake", "nanobind-config.cmake")
        # tsl-robin-map has been unvendored, skip a check for its presence
        replace_in_file(self, cmakelists, "if (NOT IS_DIRECTORY", "if (FALSE AND NOT IS_DIRECTORY")
        # Force building of nanobind lib
        save(self, cmakelists, f"\nnanobind_build_library({self._libname})", append=True)
        # Link against tsl-robin-map and install the lib and headers
        replace_in_file(self, nb_config,
            "target_include_directories(${TARGET_NAME} PRIVATE\n    ${NB_DIR}/ext/robin_map/include)\n",
            (
                "find_package(tsl-robin-map REQUIRED CONFIG)\n"
                "target_link_libraries(${TARGET_NAME} PRIVATE tsl::robin_map)\n"
                "include(GNUInstallDirs)\n"
                "install(TARGETS ${TARGET_NAME})\n"
                "install(DIRECTORY ${NB_DIR}/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})\n"
            ),
        )
        # No need to build the lib inside nanobind_add_module() call
        replace_in_file(self, nb_config, "nanobind_build_library(${libname})\n", "")
        # Link against previously built nanobind and Python
        # FIXME: the CPython include dirs should be added by Conan automatically
        replace_in_file(self, nb_config,
            "target_link_libraries(${name} PRIVATE ${libname})\n",
            (
                "target_link_libraries(${name} PRIVATE nanobind::nanobind)\n"
                "target_include_directories(${name} PUBLIC ${Python_INCLUDE_DIRS})\n"
            ),
        )
        # Propagate options to nanobind_add_module()
        replace_in_file(self, nb_config, "add_library(${name}",
             (
                 f"set(ARG_NB_SHARED {str(self.options.shared).upper()})\n"
                 f"set(ARG_NB_STATIC {str(not self.options.shared).upper()})\n"
                 f"set(ARG_STABLE_ABI {str(self.options.stable_abi).upper()})\n"
                 + (f"set(ARG_NB_DOMAIN {self.options.domain})\n" if self.options.domain else "")
                 + "add_library(${name}"
             ),
        )

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        copy(self, "nanobind-config.cmake",
             src=os.path.join(self.source_folder, "cmake"),
             dst=os.path.join(self.package_folder, "lib", "cmake"))
        rename(self,
               os.path.join(self.package_folder, "lib", "cmake", "nanobind-config.cmake"),
               os.path.join(self.package_folder, "lib", "cmake", "nanobind-conan-config.cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        self.cpp_info.builddirs = [os.path.join(self.package_folder, "lib", "cmake")]
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "nanobind-conan-config.cmake")])
