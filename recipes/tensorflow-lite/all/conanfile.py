import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.36.0"


class TensorflowLiteConan(ConanFile):
    name = "tensorflow-lite"
    version = "2.6.0"
    license = "Apache 2.0"
    homepage = "https://www.tensorflow.org/lite/guide"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("TensorFlow Lite is a set of tools that enables on-device machine learning "
                   "by helping developers run their models on mobile, embedded, and IoT devices.")
    topics = ("machine learning", "neural networks", "deep learning")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ruy": [True, False],
        "with_nnapi": [True, False],
        "with_mmap": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ruy": False,
        "with_nnapi": False,
        "with_mmap": True
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/**"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_nnapi
            del self.options.with_mmap
        if self.settings.os == "Macos":
            del self.options.with_nnapi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")

    def requirements(self):
        self.requires("abseil/20210324.2")
        self.requires("eigen/3.4.0")
        self.requires("farmhash/cci.20190513")
        self.requires("fft/cci.20061228")
        self.requires("flatbuffers/2.0.0")
        self.requires("gemmlowp/cci.20210928")
        self.requires("intel-neon2sse/cci.20210225")
        self.requires("ruy/cci.20210622")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions.update({
            "TFLITE_ENABLE_RUY": self.options.get_safe("with_ruy", False),
            "TFLITE_ENABLE_NNAPI": self.options.get_safe("with_nnapi", False),
            "TFLITE_ENABLE_GPU": False,
            "TFLITE_ENABLE_XNNPACK": False,
            "TFLITE_ENABLE_MMAP": self.options.get_safe("with_mmap", False)
        })
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "tensorflow", "lite"), src=os.path.join(self._source_subfolder, "tensorflow", "lite"))
        self.copy("*", dst="lib", src=os.path.join(self._build_subfolder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tensorflowlite")
        self.cpp_info.set_property("cmake_target_name", "tensorflowlite")
        cxxflags = []
        if not self.options.shared:
            cxxflags.append("-DTFL_STATIC_LIBRARY_BUILD")
        if self.options.get_safe("with_ruy", False):
            cxxflags.append("-DTFLITE_WITH_RUY")

        self.cpp_info.cxxflags = cxxflags
        self.cpp_info.libs = tools.collect_libs(self)
        # necessary because gemmlowp is packaged as a shared library
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
