from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.46.0"


class KissfftConan(ConanFile):
    name = "kissfft"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mborgerding/kissfft"
    description = "a Fast Fourier Transform (FFT) library that tries to Keep it Simple, Stupid"
    topics = ("fft", "kiss", "frequency-domain", "fast-fourier-transform")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "datatype": ["float", "double", "int16_t", "int32_t", "simd"],
        "openmp": [True, False],
        "use_alloca": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "datatype": "float",
        "openmp": False,
        "use_alloca": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["KISSFFT_PKGCONFIG"] = False
        tc.variables["KISSFFT_STATIC"] = not self.options.shared
        tc.variables["KISSFFT_TEST"] = False
        tc.variables["KISSFFT_TOOLS"] = False
        tc.variables["KISSFFT_DATATYPE"] = self.options.datatype
        tc.variables["KISSFFT_OPENMP"] = self.options.openmp
        tc.variables["KISSFFT_USE_ALLOCA"] = self.options.use_alloca
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        lib_name = "kissfft-{datatype}{openmp}".format(
            datatype=self.options.datatype,
            openmp="-openmp" if self.options.openmp else "",
        )

        self.cpp_info.set_property("cmake_file_name", "kissfft")
        self.cpp_info.set_property("cmake_target_name", "kissfft::kissfft")
        self.cpp_info.set_property("cmake_target_aliases", [f"kissfft::{lib_name}"])
        self.cpp_info.set_property("pkg_config_name", lib_name)
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libkissfft"].includedirs.append(os.path.join("include", "kissfft"))
        self.cpp_info.components["libkissfft"].libs = [lib_name]

        # got to duplicate the logic from kissfft/CMakeLists.txt
        if self.options.datatype in ["float", "double"]:
            self.cpp_info.components["libkissfft"].defines.append(f"kiss_fft_scalar={self.options.datatype}")
        elif self.options.datatype == "int16_t":
            self.cpp_info.components["libkissfft"].defines.append("FIXED_POINT=16")
        elif self.options.datatype == "int32_t":
            self.cpp_info.components["libkissfft"].defines.append("FIXED_POINT=32")
        elif self.options.datatype == "simd":
            self.cpp_info.components["libkissfft"].defines.append("USE_SIMD")

        if self.options.use_alloca:
            self.cpp_info.components["libkissfft"].defines.append("KISS_FFT_USE_ALLOCA")

        if self.options.shared:
            self.cpp_info.components["libkissfft"].defines.append("KISS_FFT_SHARED")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libkissfft"].system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["pkg_config"] = lib_name
        self.cpp_info.components["libkissfft"].names["cmake_find_package"] = lib_name
        self.cpp_info.components["libkissfft"].names["cmake_find_package_multi"] = lib_name
        self.cpp_info.components["libkissfft"].set_property("cmake_target_name", "kissfft::kissfft")
        self.cpp_info.components["libkissfft"].set_property("pkg_config_name", lib_name)
