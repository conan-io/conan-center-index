from conans import CMake, ConanFile, tools
import glob
import os


class Argtable3Conan(ConanFile):
    name = "argtable3"
    description = "A single-file, ANSI C, command-line parsing library that parses GNU-style command-line options."
    topics = ("conan", "argtable3", "command", "line", "argument", "parse", "parsing", "getopt")
    license = "BSD-3-clause"
    homepage = "https://www.argtable.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    _cmake = None

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
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("argtable3-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ARGTABLE3_ENABLE_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # The initial space is important (the cmake script does OFFSET 0)
        tools.save(os.path.join(self._source_subfolder, "version.tag"), " {}.0\n".format(self.version))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["argtable3" if self.options.shared else "argtable3_static"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
        # FIXME: the cmake targets are exported without namespace
        self.cpp_info.filenames["cmake_find_package"] = "Argtable3"
        self.cpp_info.filenames["cmake_find_package_config"] = "Argtable3"
