from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conans import CMake, tools
from conan import ConanFile
from conans.errors import ConanInvalidConfiguration
import functools
import os


required_conan_version = ">=1.45.0"


class PCRE2Conan(ConanFile):
    name = "pcre2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org/"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "perl")
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
        "support_jit": [True, False],
        "support_callout_fork": [True, False],
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
        "support_jit": False,
        "support_callout_fork": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

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

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")

    def validate(self):
        if not self.options.build_pcre2_8 and not self.options.build_pcre2_16 and not self.options.build_pcre2_32:
            raise ConanInvalidConfiguration("At least one of build_pcre2_8, build_pcre2_16 or build_pcre2_32 must be enabled")
        if self.options.build_pcre2grep and not self.options.build_pcre2_8:
            raise ConanInvalidConfiguration("build_pcre2_8 must be enabled for the pcre2grep program")

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

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if tools.Version(self.version) >= "10.38":
            cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["PCRE2_BUILD_PCRE2GREP"] = self.options.build_pcre2grep
        cmake.definitions["PCRE2_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        cmake.definitions["PCRE2_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        cmake.definitions["PCRE2_BUILD_TESTS"] = False
        if is_msvc(self):
            cmake.definitions["PCRE2_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
        cmake.definitions["PCRE2_DEBUG"] = self.settings.build_type == "Debug"
        cmake.definitions["PCRE2_BUILD_PCRE2_8"] = self.options.build_pcre2_8
        cmake.definitions["PCRE2_BUILD_PCRE2_16"] = self.options.build_pcre2_16
        cmake.definitions["PCRE2_BUILD_PCRE2_32"] = self.options.build_pcre2_32
        cmake.definitions["PCRE2_SUPPORT_JIT"] = self.options.support_jit
        cmake.definitions["PCRE2GREP_SUPPORT_CALLOUT_FORK"] = self.options.support_callout_fork
        if tools.Version(self.version) < "10.38":
            # relocatable shared libs on Macos
            cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "man"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PCRE2")
        self.cpp_info.set_property("pkg_config_name", "libpcre2")
        if self.options.build_pcre2_8:
            # pcre2-8
            self.cpp_info.components["pcre2-8"].set_property("cmake_target_name", "PCRE2::8BIT")
            self.cpp_info.components["pcre2-8"].set_property("pkg_config_name", "libpcre2-8")
            self.cpp_info.components["pcre2-8"].libs = [self._lib_name("pcre2-8")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-8"].defines.append("PCRE2_STATIC")
            # pcre2-posix
            self.cpp_info.components["pcre2-posix"].set_property("cmake_target_name", "PCRE2::POSIX")
            self.cpp_info.components["pcre2-posix"].set_property("pkg_config_name", "libpcre2-posix")
            self.cpp_info.components["pcre2-posix"].libs = [self._lib_name("pcre2-posix")]
            self.cpp_info.components["pcre2-posix"].requires = ["pcre2-8"]
        # pcre2-16
        if self.options.build_pcre2_16:
            self.cpp_info.components["pcre2-16"].set_property("cmake_target_name", "PCRE2::16BIT")
            self.cpp_info.components["pcre2-16"].set_property("pkg_config_name", "libpcre2-16")
            self.cpp_info.components["pcre2-16"].libs = [self._lib_name("pcre2-16")]
            if not self.options.shared:
                self.cpp_info.components["pcre2-16"].defines.append("PCRE2_STATIC")
        # pcre2-32
        if self.options.build_pcre2_32:
            self.cpp_info.components["pcre2-32"].set_property("cmake_target_name", "PCRE2::32BIT")
            self.cpp_info.components["pcre2-32"].set_property("pkg_config_name", "libpcre2-32")
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

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generator removed
        self.cpp_info.names["cmake_find_package"] = "PCRE2"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE2"
        self.cpp_info.names["pkg_config"] = "libpcre2"
        if self.options.build_pcre2_8:
            self.cpp_info.components["pcre2-8"].names["cmake_find_package"] = "8BIT"
            self.cpp_info.components["pcre2-8"].names["cmake_find_package_multi"] = "8BIT"
            self.cpp_info.components["pcre2-posix"].names["cmake_find_package"] = "POSIX"
            self.cpp_info.components["pcre2-posix"].names["cmake_find_package_multi"] = "POSIX"
        if self.options.build_pcre2_16:
            self.cpp_info.components["pcre2-16"].names["cmake_find_package"] = "16BIT"
            self.cpp_info.components["pcre2-16"].names["cmake_find_package_multi"] = "16BIT"
        if self.options.build_pcre2_32:
            self.cpp_info.components["pcre2-32"].names["cmake_find_package"] = "32BIT"
            self.cpp_info.components["pcre2-32"].names["cmake_find_package_multi"] = "32BIT"

    def _lib_name(self, name):
        libname = name
        if tools.Version(self.version) >= "10.38" and is_msvc(self) and not self.options.shared:
            libname += "-static"
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                libname += "d"
            if self.settings.compiler == "gcc" and self.options.shared:
                libname += ".dll"
        return libname
