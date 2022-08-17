from conan import ConanFile
from conan.tools import files
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conan.errors import ConanInvalidConfiguration
from conans import CMake, tools
import functools
import os

required_conan_version = ">=1.36.0"


class PCREConan(ConanFile):
    name = "pcre"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "PCRE")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_pcre_8": [True, False],
        "build_pcre_16": [True, False],
        "build_pcre_32": [True, False],
        "build_pcrecpp": [True, False],
        "build_pcregrep": [True, False],
        "with_bzip2": [True, False],
        "with_zlib": [True, False],
        "with_jit": [True, False],
        "with_utf": [True, False],
        "with_unicode_properties": [True, False],
        "with_stack_for_recursion": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_pcre_8": True,
        "build_pcre_16": True,
        "build_pcre_32": True,
        "build_pcrecpp": False,
        "build_pcregrep": True,
        "with_bzip2": True,
        "with_zlib": True,
        "with_jit": False,
        "with_utf": True,
        "with_unicode_properties": True,
        "with_stack_for_recursion": True,
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
        if not self.options.build_pcrecpp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if not self.options.build_pcregrep:
            del self.options.with_bzip2
            del self.options.with_zlib
        if self.options.with_unicode_properties:
            self.options.with_utf = True

    def requirements(self):
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.12")

    def validate(self):
        if not self.options.build_pcre_8 and not self.options.build_pcre_16 and not self.options.build_pcre_32:
            raise ConanInvalidConfiguration("At least one of build_pcre_8, build_pcre_16 or build_pcre_32 must be enabled")
        if self.options.build_pcrecpp and not self.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the C++ library support")
        if self.options.build_pcregrep and not self.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the pcregrep program")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        cmake_file = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Avoid man and share during install stage
        files.replace_in_file(self,
            cmake_file, "INSTALL(FILES ${man1} DESTINATION man/man1)", "")
        files.replace_in_file(self,
            cmake_file, "INSTALL(FILES ${man3} DESTINATION man/man3)", "")
        files.replace_in_file(self,
            cmake_file, "INSTALL(FILES ${html} DESTINATION share/doc/pcre/html)", "")
        # Do not override CMAKE_MODULE_PATH and do not add ${PROJECT_SOURCE_DIR}/cmake
        # because it contains a custom FindPackageHandleStandardArgs.cmake which
        # can break conan generators
        files.replace_in_file(self,
            cmake_file, "SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)", "")
        # Avoid CMP0006 error (macos bundle)
        files.replace_in_file(self,
            cmake_file, "RUNTIME DESTINATION bin", "RUNTIME DESTINATION bin\n        BUNDLE DESTINATION bin")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PCRE_BUILD_TESTS"] = False
        cmake.definitions["PCRE_BUILD_PCRE8"] = self.options.build_pcre_8
        cmake.definitions["PCRE_BUILD_PCRE16"] = self.options.build_pcre_16
        cmake.definitions["PCRE_BUILD_PCRE32"] = self.options.build_pcre_32
        cmake.definitions["PCRE_BUILD_PCREGREP"] = self.options.build_pcregrep
        cmake.definitions["PCRE_BUILD_PCRECPP"] = self.options.build_pcrecpp
        cmake.definitions["PCRE_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        cmake.definitions["PCRE_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        cmake.definitions["PCRE_SUPPORT_JIT"] = self.options.with_jit
        cmake.definitions["PCRE_SUPPORT_UTF"] = self.options.with_utf
        cmake.definitions["PCRE_SUPPORT_UNICODE_PROPERTIES"] = self.options.with_unicode_properties
        cmake.definitions["PCRE_SUPPORT_LIBREADLINE"] = False
        cmake.definitions["PCRE_SUPPORT_LIBEDIT"] = False
        cmake.definitions["PCRE_NO_RECURSE"] = not self.options.with_stack_for_recursion
        if is_msvc(self):
            cmake.definitions["PCRE_STATIC_RUNTIME"] = "MT" in msvc_runtime_flag(self)
        if tools.is_apple_os(self.settings.os):
            # Generate a relocatable shared lib on Macos
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
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PCRE"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE"
        if self.options.build_pcre_8:
            # pcre
            self.cpp_info.components["libpcre"].set_property("pkg_config_name", "libpcre")
            self.cpp_info.components["libpcre"].libs = [self._lib_name("pcre")]
            if not self.options.shared:
                self.cpp_info.components["libpcre"].defines.append("PCRE_STATIC=1")
            # pcreposix
            self.cpp_info.components["libpcreposix"].set_property("pkg_config_name", "libpcreposix")
            self.cpp_info.components["libpcreposix"].libs = [self._lib_name("pcreposix")]
            self.cpp_info.components["libpcreposix"].requires = ["libpcre"]
            # pcrecpp
            if self.options.build_pcrecpp:
                self.cpp_info.components["libpcrecpp"].set_property("pkg_config_name", "libpcrecpp")
                self.cpp_info.components["libpcrecpp"].libs = [self._lib_name("pcrecpp")]
                self.cpp_info.components["libpcrecpp"].requires = ["libpcre"]
        # pcre16
        if self.options.build_pcre_16:
            self.cpp_info.components["libpcre16"].set_property("pkg_config_name", "libpcre16")
            self.cpp_info.components["libpcre16"].libs = [self._lib_name("pcre16")]
            if not self.options.shared:
                self.cpp_info.components["libpcre16"].defines.append("PCRE_STATIC=1")
        # pcre32
        if self.options.build_pcre_32:
            self.cpp_info.components["libpcre32"].set_property("pkg_config_name", "libpcre32")
            self.cpp_info.components["libpcre32"].libs = [self._lib_name("pcre32")]
            if not self.options.shared:
                self.cpp_info.components["libpcre32"].defines.append("PCRE_STATIC=1")

        if self.options.build_pcregrep:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
            # FIXME: This is a workaround to avoid ConanException. zlib and bzip2
            # are optional requirements of pcregrep executable, not of any pcre lib.
            if self.options.with_bzip2:
                self.cpp_info.components["libpcre"].requires.append("bzip2::bzip2")
            if self.options.with_zlib:
                self.cpp_info.components["libpcre"].requires.append("zlib::zlib")

    def _lib_name(self, name):
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            return name + "d"
        return name
