from conans import ConanFile, CMake, tools


class ClspvConan(ConanFile):
    name = "clspv"
    version = "0.1"
    license = "Apache 2.0 license."
    homepage = "https://github.com/google/clspv"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A prototype compiler for a subset of OpenCL C to Vulkan compute shaders."
    topics = ("vulkan", "opencl", "spirv", "spir", "vulkan-compute-shaders")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone https://github.com/google/clspv.git")
        self.run("./clspv/utils/fetch_sources.py")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="clspv")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["clspv_combined"]

