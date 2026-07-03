from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir

import os

required_conan_version = ">=2"


class CryptoPPModernConan(ConanFile):
    name = "cryptopp-modern"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cryptopp-modern/cryptopp-modern"
    license = "BSL-1.0"
    description = "An actively maintained fork of Crypto++ that modernizes the build system and codebase."
    topics = ("crypto", "cryptographic", "security")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_openmp": False,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.use_openmp:
            # cryptopp links OpenMP into the (static) library, so the runtime must
            # be propagated to consumers. Depend on the OpenMP runtime explicitly
            # instead of relying on a system/Homebrew libomp being present.
            self.requires("llvm-openmp/20.1.6")

    def validate(self):
        # Crypto++ does not properly support shared/DLL builds; the bundled CMake
        # errors out when CRYPTOPP_BUILD_SHARED is enabled.
        if self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared builds")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Honor the fPIC option instead of the unconditional PIC the project forces.
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE 1)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CRYPTOPP_BUILD_TESTING"] = False
        tc.cache_variables["CRYPTOPP_USE_INTERMEDIATE_OBJECTS_TARGET"] = False
        tc.cache_variables["CRYPTOPP_USE_OPENMP"] = self.options.use_openmp
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Git"] = True
        if self.options.use_openmp:
            # Make the project's find_package(OpenMP) resolve to the llvm-openmp
            # Conan package (config mode) rather than a system libomp.
            tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cryptopp-modern")
        self.cpp_info.set_property("cmake_target_name", "cryptopp::cryptopp")
        self.cpp_info.set_property("pkg_config_name", "cryptopp-modern")

        self.cpp_info.libs = ["cryptopp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["bcrypt", "ws2_32"]
        # When use_openmp is enabled the OpenMP runtime is pulled in (and
        # propagated to consumers) via the llvm-openmp dependency.
