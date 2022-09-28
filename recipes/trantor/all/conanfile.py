from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.52.0"

class TrantorConan(ConanFile):
    name = "trantor"
    description = "a non-blocking I/O tcp network lib based on c++14/17"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/an-tao/trantor"
    topics = ("tcp-server", "asynchronous-programming", "non-blocking-io")
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_c_ares": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_c_ares": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/1.1.1q")
        if self.options.with_c_ares:
            self.requires("c-ares/1.18.1")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version:
            if Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
        else:
            self.output.warn(f"{self.ref} requires C++{self._minimum_cpp_standard}. Your compiler is unknown. Assuming it supports C++{self._minimum_cpp_standard}.")

        # TODO: Compilation succeeds, but execution of test_package fails on Visual Studio 16 MDd
        if is_msvc(self) and Version(self.info.settings.compiler.version) == "16" and \
           self.options.shared and self.info.settings.compiler.runtime == "MDd":
            raise ConanInvalidConfiguration(f"{self.ref} does not support the MDd runtime on Visual Studio 16.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "1.5.6":
            tc.variables["BUILD_TRANTOR_SHARED"] = self.options.shared
        else:
            # Trantor's CMakeaLists.txt has BUILD_SHARED_LIBS option.
            tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_C-ARES"] = self.options.with_c_ares
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # fix c-ares imported target
        replace_in_file(self, cmakelists, "c-ares_lib", "c-ares::cares")
        # Cleanup rpath in shared lib
        replace_in_file(self, cmakelists, "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${INSTALL_LIB_DIR}\")", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Trantor")
        self.cpp_info.set_property("cmake_target_name", "Trantor::Trantor")
        self.cpp_info.libs = ["trantor"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Trantor"
        self.cpp_info.names["cmake_find_package_multi"] = "Trantor"
