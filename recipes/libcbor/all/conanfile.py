import os
from conans import CMake, ConanFile, tools

required_conan_version = ">=1.33.0"

class LibCborStackConan(ConanFile):
    name = "libcbor"
    license = "MIT"
    homepage = "https://github.com/PJK/libcbor"
    url = "https://github.com/conan-io/conan-center-index"
    description = """CBOR protocol implementation for C"""
    topics = ("cbor", "serialization", "messaging")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "custom_alloc": [True, False],
        "pretty_printer": [True, False],
        "buffer_growth_factor": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "custom_alloc": False,
        "pretty_printer": True,
        "buffer_growth_factor": 2,
    }
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_EXAMPLES"] = False
        self._cmake.definitions["SANITIZE"] = False
        self._cmake.definitions["CBOR_CUSTOM_ALLOC"] = self.options.custom_alloc
        self._cmake.definitions["CBOR_PRETTY_PRINTER"] = self.options.pretty_printer
        self._cmake.definitions["CBOR_BUFFER_GROWTH"] = self.options.buffer_growth_factor

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
