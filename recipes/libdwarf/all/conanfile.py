from conans import ConanFile, CMake, tools
import os


class LibdwarfConan(ConanFile):
    name = "libdwarf"
    description = "A library and a set of command-line tools for reading and writing DWARF2"
    topics = ("conan", "libdwarf", "dwarf2", "debugging", "dwarf")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.prevanders.net/dwarf.html"
    license = "LGPL-2.1"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = ("libelf/0.8.13", "zlib/1.2.11")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.mkdir(os.path.join(self.build_folder, self._build_subfolder))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "libdwarf"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
