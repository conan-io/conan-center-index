import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration


class LibelfinConan(ConanFile):
    name = "libelfin"
    description = "C++11 library for reading ELF binaries and DWARFv4 debug information"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aclements/libelfin"
    license = "MIT"
    topics = ("conan", "elf", "dwarf", "libelfin")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    _cmake = None
    _source_subfolder = "source_subfolder"

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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libelf++"].names["pkg_config"] = "libelf++"
        self.cpp_info.components["libelf++"].libs = ["elf++"]
        self.cpp_info.components["libdwarf++"].names["pkg_config"] = "libdwarf++"
        self.cpp_info.components["libdwarf++"].libs = ["dwarf++"]
        self.cpp_info.components["libdwarf++"].requires = ["libelf++"]
