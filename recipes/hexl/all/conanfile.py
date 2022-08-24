from conan import ConanFile
from conans import CMake
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, rmdir
from conan.tools.scm import Version
from conan.tools.build import cross_building

import os

required_conan_version = ">=1.43.0"

class HexlConan(ConanFile):
    name = "hexl"
    license = "Apache-2.0"
    homepage = "https://github.com/intel/hexl"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Intel Homomorphic Encryption (HE) Acceleration Library"
    topics = ("homomorphic", "encryption", "privacy")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "experimental": [True, False],
        "fpga_compatibility_dyadic_multiply": [True, False],
        "fpga_compatibility_keyswitch":  [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "experimental": False,
        "fpga_compatibility_dyadic_multiply": False,
        "fpga_compatibility_keyswitch": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        self.build_requires("cmake/3.22.0")

    def requirements(self):
        self.requires("cpu_features/0.7.0")

        if self.settings.build_type == "Debug":
            self.requires("easyloggingpp/9.97.0")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7",
            "clang": "7",
            "apple-clang": "11",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Hexl only supports x86 architecture")

        if self.options.shared and is_msvc(self):
            raise ConanInvalidConfiguration("Hexl only supports static linking with msvc")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self);


        self._cmake.definitions["HEXL_BENCHMARK"] = False
        self._cmake.definitions["HEXL_TESTING"] = False
        self._cmake.definitions["HEXL_EXPERIMENTAL"] = self.options.experimental


        if self.options.fpga_compatibility_dyadic_multiply and self.options.fpga_compatibility_keyswitch:
            self._cmake.definitions["HEXL_FPGA_COMPATIBILITY"] = 3
        elif self.options.fpga_compatibility_dyadic_multiply:
            self._cmake.definitions["HEXL_FPGA_COMPATIBILITY"] = 1
        elif self.options.fpga_compatibility_keyswitch:
            self._cmake.definitions["HEXL_FPGA_COMPATIBILITY"] = 2
        else:
            self._cmake.definitions["HEXL_FPGA_COMPATIBILITY"] = 0

        self._cmake.definitions["HEXL_SHARED_LIB"] = self.options.shared
        self._cmake.definitions["HEXL_CROSS_COMPILED"] = cross_building(self)

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Hexl")
        # TODO: Remove in Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "Hexl"
        self.cpp_info.names["cmake_find_package_multi"] = "Hexl"

        if self.settings.build_type == "Debug":
            if not is_msvc(self):
                self.cpp_info.components["Hexl"].libs = ["hexl_debug"]
            else:
                self.cpp_info.components["Hexl"].libs = ["hexl"]

            self.cpp_info.components["Hexl"].requires.append("easyloggingpp::easyloggingpp")
        else:
            self.cpp_info.components["Hexl"].libs = ["hexl"]

        self.cpp_info.components["Hexl"].names["cmake_find_package"] = "hexl"
        self.cpp_info.components["Hexl"].names["cmake_find_package_multi"] = "hexl"
        self.cpp_info.components["Hexl"].set_property("cmake_target_name", "Hexl::hexl")
        self.cpp_info.components["Hexl"].set_property("pkg_config_name", "hexl")
        self.cpp_info.components["Hexl"].requires.append("cpu_features::libcpu_features")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["Hexl"].system_libs = ["pthread", "m"]

