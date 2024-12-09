from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get
import os

class otfftppRecipe(ConanFile):
    name = "robinchrist-otfftpp"
    package_type = "library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/robinchrist/otfftpp"
    description = "OTFFT is a high-speed FFT library using the Stockham's algorithm and SIMD"
    topics = ("FFT", "SIMD")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "abi_affecting_cflags": ["ANY"], #comma separated list of c-flags, will be converted to a set for normalization and sorting
        "abi_affecting_cxxflags": ["ANY"], #comma separated list of c-flags, will be converted to a set for normalization and sorting
        "with_openmp": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "abi_affecting_cflags": "",
        "abi_affecting_cxxflags": "",
        "with_openmp": False
    }

    def _abi_affecting_cflags(self, info=False):
        options = self.info.options if info else self.options
        return sorted(set(str(options.abi_affecting_cflags).split(",")))

    def _abi_affecting_cxxflags(self, info=False):
        options = self.info.options if info else self.options
        return sorted(set(str(options.abi_affecting_cxxflags).split(",")))

    @property
    def _openmp_flags(self):
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        elif is_msvc(self):
            return ["-openmp"]
        return None

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("simde/0.8.2")

        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.6", transitive_headers=True, transitive_libs=True)

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)

        tc.variables["OTFFTPP_WITH_OPENMP"] = self.options.with_openmp
        tc.variables["OTFFTPP_BUILD_TESTS"] = False

        tc.extra_cflags.extend(self._abi_affecting_cflags())
        tc.extra_cxxflags.extend(self._abi_affecting_cxxflags())

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        # normalize the the extra flags (sorted+comma separated)
        self.info.options.abi_affecting_cflags = ",".join(self._abi_affecting_cflags(info=True))
        self.info.options.abi_affecting_cxxflags = ",".join(self._abi_affecting_cxxflags(info=True))

    def package_info(self):
        self.cpp_info.libs = ["otfftpp"]

        if self.options.with_openmp:
            if self.settings.compiler in ["clang", "apple-clang"]:
                self.cpp_info.requires.append("llvm-openmp::llvm-openmp")
            openmp_flags = self._openmp_flags
            self.cpp_info.cflags = openmp_flags
            self.cpp_info.cxxflags = openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags
            self.cpp_info.exelinkflags = openmp_flags
