from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

required_conan_version = ">=1.43.0"


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

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["KISSFFT_PKGCONFIG"] = False
        cmake.definitions["KISSFFT_STATIC"] = not self.options.shared
        cmake.definitions["KISSFFT_TEST"] = False
        cmake.definitions["KISSFFT_TOOLS"] = False
        cmake.definitions["KISSFFT_DATATYPE"] = self.options.datatype
        cmake.definitions["KISSFFT_OPENMP"] = self.options.openmp
        cmake.definitions["KISSFFT_USE_ALLOCA"] = self.options.use_alloca
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        lib_name = "kissfft-{datatype}{openmp}".format(
            datatype=self.options.datatype,
            openmp="-openmp" if self.options.openmp else "",
        )

        self.cpp_info.set_property("cmake_file_name", "kissfft")
        self.cpp_info.set_property("cmake_target_name", "kissfft::kissfft")
        self.cpp_info.set_property("cmake_target_aliases", ["kissfft::{}".format(lib_name)])
        self.cpp_info.set_property("pkg_config_name", lib_name)
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libkissfft"].includedirs.append(os.path.join("include", "kissfft"))
        self.cpp_info.components["libkissfft"].libs = [lib_name]

        # got to duplicate the logic from kissfft/CMakeLists.txt
        if self.options.datatype in ["float", "double"]:
            self.cpp_info.components["libkissfft"].defines.append("kiss_fft_scalar={}".format(self.options.datatype))
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
