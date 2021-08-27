from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PCRE2Conan(ConanFile):
    name = "pcre2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org/"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "PCRE")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "build_pcre2grep": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "support_jit": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_pcre2_8": True,
        "build_pcre2_16": True,
        "build_pcre2_32": True,
        "build_pcre2grep": True,
        "with_zlib": True,
        "with_bzip2": True,
        "support_jit": False
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.build_pcre2grep:
            del self.options.with_zlib
            del self.options.with_bzip2
        if not self.options.build_pcre2_8 and not self.options.build_pcre2_16 and not self.options.build_pcre2_32:
            raise ConanInvalidConfiguration("At least one of build_pcre2_8, build_pcre2_16 or build_pcre2_32 must be enabled")
        if self.options.build_pcre2grep and not self.options.build_pcre2_8:
            raise ConanInvalidConfiguration("build_pcre2_8 must be enabled for the pcre2grep program")

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Do not add ${PROJECT_SOURCE_DIR}/cmake because it contains a custom
        # FindPackageHandleStandardArgs.cmake which can break conan generators
        if tools.Version(self.version) < "10.34":
            tools.replace_in_file(cmakelists, "SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        else:
            tools.replace_in_file(cmakelists, "LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        # Avoid CMP0006 error (macos bundle)
        tools.replace_in_file(cmakelists,
                              "RUNTIME DESTINATION bin",
                              "RUNTIME DESTINATION bin BUNDLE DESTINATION bin")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["PCRE2_BUILD_PCRE2GREP"] = self.options.build_pcre2grep
        self._cmake.definitions["PCRE2_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        self._cmake.definitions["PCRE2_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        self._cmake.definitions["PCRE2_BUILD_TESTS"] = False
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            runtime = not self.options.shared and "MT" in self.settings.compiler.runtime
            self._cmake.definitions["PCRE2_STATIC_RUNTIME"] = runtime
        self._cmake.definitions["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        self._cmake.definitions["PCRE2_BUILD_PCRE2_8"] = self.options.build_pcre2_8
        self._cmake.definitions["PCRE2_BUILD_PCRE2_16"] = self.options.build_pcre2_16
        self._cmake.definitions["PCRE2_BUILD_PCRE2_32"] = self.options.build_pcre2_32
        self._cmake.definitions["PCRE2_SUPPORT_JIT"] = self.options.support_jit
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        cmake.patch_config_paths()
        tools.rmdir(os.path.join(self.package_folder, "man"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libpcre2"
        if self.options.build_pcre2_8:
            # pcre2-8
            self.cpp_info.components["pcre2-8"].names["pkg_config"] = "libpcre2-8"
            self.cpp_info.components["pcre2-8"].libs = [self._lib_name("pcre2-8")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-8"].defines.append("PCRE2_STATIC")
            # pcre2-posix
            self.cpp_info.components["pcre2-posix"].names["pkg_config"] = "libpcre2-posix"
            self.cpp_info.components["pcre2-posix"].libs = [self._lib_name("pcre2-posix")]
            self.cpp_info.components["pcre2-posix"].requires = ["pcre2-8"]
        # pcre2-16
        if self.options.build_pcre2_16:
            self.cpp_info.components["pcre2-16"].names["pkg_config"] = "libpcre2-16"
            self.cpp_info.components["pcre2-16"].libs = [self._lib_name("pcre2-16")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-16"].defines.append("PCRE2_STATIC")
        # pcre2-32
        if self.options.build_pcre2_32:
            self.cpp_info.components["pcre2-32"].names["pkg_config"] = "libpcre2-32"
            self.cpp_info.components["pcre2-32"].libs = [self._lib_name("pcre2-32")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-32"].defines.append("PCRE2_STATIC")

        if self.options.build_pcre2grep:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
            # FIXME: This is a workaround to avoid ConanException. zlib and bzip2
            # are optional requirements of pcre2grep executable, not of any pcre2 lib.
            if self.options.with_zlib:
                self.cpp_info.components["pcre2-8"].requires.append("zlib::zlib")
            if self.options.with_bzip2:
                self.cpp_info.components["pcre2-8"].requires.append("bzip2::bzip2")

    def _lib_name(self, name):
        libname = name
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                libname += "d"
            if self.settings.compiler == "gcc" and self.options.shared:
                libname += ".dll"
        return libname
