from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
import os


class AsyncppRecipe(ConanFile):
    name = "asyncpp"

    # Optional metadata
    license = "MIT"
    author = "Péter Kardos"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://github.com/petiaccja/asyncpp"
    description = "A C++20 coroutine library for asynchronous and parallel programming."
    topics = ("coroutine", "c++20", "async", "parallel", "concurrency")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def validate(self):
        tools.build.check_min_cppstd(self, "20")

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")
    
    def source(self):
        tools.files.get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            variables={
                "ASYNCPP_BUILD_TESTS": "OFF",
                "ASYNCPP_BUILD_BENCHMARKS": "OFF"
            },
            build_script_folder=self._source_subfolder
        )
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        dst_lic_folder = os.path.join(self.package_folder, "licenses")
        tools.files.copy(self, "LICENSE.md", dst=dst_lic_folder, src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["asyncpp"]