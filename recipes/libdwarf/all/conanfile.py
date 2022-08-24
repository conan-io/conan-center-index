from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.33.0"


class LibdwarfConan(ConanFile):
    name = "libdwarf"
    description = "A library and a set of command-line tools for reading and writing DWARF2"
    topics = ("libdwarf", "dwarf2", "debugging", "dwarf")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.prevanders.net/dwarf.html"
    license = "LGPL-2.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"

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

    def requirements(self):
        self.requires("libelf/0.8.13")
        self.requires("zlib/1.2.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_NON_SHARED"] = not self.options.shared
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.definitions["BUILD_DWARFGEN"] = False
        cmake.definitions["BUILD_DWARFEXAMPLE"] = False
        if tools.cross_building(self):
            cmake.definitions["HAVE_UNUSED_ATTRIBUTE_EXITCODE"] = "0"
            cmake.definitions["HAVE_UNUSED_ATTRIBUTE_EXITCODE__TRYRUN_OUTPUT"] = ""
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "libdwarf"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dwarf"]
