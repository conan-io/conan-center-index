import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake

required_conan_version = ">=1.36.0"

class HeatshrinkConan(ConanFile):
    name = "heatshrink"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    description = "data compression library for embedded/real-time systems"
    topics = ("compression", "embedded", "realtime")
    homepage = "https://github.com/atomicobject/heatshrink"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    options = {
        "shared": [False, True],
        "fPIC": [True, False],
        "dynamic_alloc": [True, False],
        "debug_log": [True, False],
        "use_index": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dynamic_alloc": True,
        "debug_log": False,
        "use_index": True,
    }

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
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        config_file = os.path.join(self._source_subfolder, "heatshrink_config.h")
        if not self.options.dynamic_alloc:
            tools.replace_in_file(config_file,
                "#define HEATSHRINK_DYNAMIC_ALLOC 1",
                "#define HEATSHRINK_DYNAMIC_ALLOC 0")
        if self.options.debug_log:
            tools.replace_in_file(config_file,
                "#define HEATSHRINK_DEBUGGING_LOGS 0",
                "#define HEATSHRINK_DEBUGGING_LOGS 1")
        if not self.options.use_index:
            tools.replace_in_file(config_file,
                "#define HEATSHRINK_USE_INDEX 1",
                "#define HEATSHRINK_USE_INDEX 0")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", "licenses", self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["heatshrink"]

