import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibelfinConan(ConanFile):
    name = "libelfin"
    description = "C++11 library for reading ELF binaries and DWARFv4 debug information"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aclements/libelfin"
    license = "MIT"
    topics = ("conan", "elf", "dwarf", "libelfin")

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt", "patches/*"

    _source_subfolder = "source_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libelfin doesn't support compiler: {} on OS: {}.".
                                            format(self.settings.compiler, self.settings.os))
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        if self.should_build:
            cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dwarf++", "elf++"]
