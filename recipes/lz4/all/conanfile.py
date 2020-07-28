from conans import CMake, ConanFile, tools
import os


class LZ4Conan(ConanFile):
    name = "lz4"
    description = "Extremely Fast Compression algorithm"
    license = ("BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lz4/lz4"
    topics = ("conan", "lz4", "compression")
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        extracted_folder = "{0}-{1}".format(self.name, self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LZ4_BUNDLED_MODE"] = False
        cmake.definitions["LZ4_POSITION_INDEPENDENT_LIB"] = self.options.get_safe("fPIC", True)
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        # Disable building and installing programs by default
        cmakefile = os.path.join(self._source_subfolder, "contrib", "cmake_unofficial", "CMakeLists.txt")
        tools.replace_in_file(cmakefile, "set(LZ4_PROGRAMS_BUILT lz4cli)", "")
        tools.replace_in_file(cmakefile, "list(APPEND LZ4_PROGRAMS_BUILT lz4c)", "")
        tools.save(cmakefile,
                   "set_target_properties(lz4c PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)\n"
                   "set_target_properties(lz4cli PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)",
                   append=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "liblz4"
        self.cpp_info.libs = ["lz4"]
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.defines.append("LZ4_DLL_IMPORT")
