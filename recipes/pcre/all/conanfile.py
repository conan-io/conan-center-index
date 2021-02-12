from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class PCREConan(ConanFile):
    name = "pcre"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org"
    description = "Perl Compatible Regular Expressions"
    topics = ("regex", "regexp", "PCRE")
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
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
        "with_stack_for_recursion": [True, False]
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
        "with_utf": False,
        "with_unicode_properties": False,
        "with_stack_for_recursion": True
    }

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
        if not self.options.build_pcrecpp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if not self.options.build_pcregrep:
            del self.options.with_bzip2
            del self.options.with_zlib
        if not self.options.build_pcre_8 and not self.options.build_pcre_16 and not self.options.build_pcre_32:
            raise ConanInvalidConfiguration("At least one of build_pcre_8, build_pcre_16 or build_pcre_32 must be enabled")
        if self.options.build_pcrecpp and not self.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the C++ library support")
        if self.options.build_pcregrep and not self.options.build_pcre_8:
            raise ConanInvalidConfiguration("build_pcre_8 must be enabled for the pcregrep program")
        if self.options.with_unicode_properties:
            self.options.with_utf = True

    def requirements(self):
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def patch_cmake(self):
        """Patch CMake file to avoid man and share during install stage
        """
        cmake_file = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(
            cmake_file, "INSTALL(FILES ${man1} DESTINATION man/man1)", "")
        tools.replace_in_file(
            cmake_file, "INSTALL(FILES ${man3} DESTINATION man/man3)", "")
        tools.replace_in_file(
            cmake_file, "INSTALL(FILES ${html} DESTINATION share/doc/pcre/html)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PCRE_BUILD_TESTS"] = False
        self._cmake.definitions["PCRE_BUILD_PCRE8"] = self.options.build_pcre_8
        self._cmake.definitions["PCRE_BUILD_PCRE16"] = self.options.build_pcre_16
        self._cmake.definitions["PCRE_BUILD_PCRE32"] = self.options.build_pcre_32
        self._cmake.definitions["PCRE_BUILD_PCREGREP"] = self.options.build_pcregrep
        self._cmake.definitions["PCRE_BUILD_PCRECPP"] = self.options.build_pcrecpp
        self._cmake.definitions["PCRE_SUPPORT_LIBZ"] = self.options.get_safe("with_zlib", False)
        self._cmake.definitions["PCRE_SUPPORT_LIBBZ2"] = self.options.get_safe("with_bzip2", False)
        self._cmake.definitions["PCRE_SUPPORT_JIT"] = self.options.with_jit
        self._cmake.definitions["PCRE_SUPPORT_UTF"] = self.options.with_utf
        self._cmake.definitions["PCRE_SUPPORT_UNICODE_PROPERTIES"] = self.options.with_unicode_properties
        self._cmake.definitions["PCRE_SUPPORT_LIBREADLINE"] = False
        self._cmake.definitions["PCRE_SUPPORT_LIBEDIT"] = False
        self._cmake.definitions["PCRE_NO_RECURSE"] = not self.options.with_stack_for_recursion
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._cmake.definitions["PCRE_STATIC_RUNTIME"] = not self.options.shared and "MT" in self.settings.compiler.runtime
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self.patch_cmake()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PCRE"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE"
        if self.options.build_pcre_8:
            # pcre
            self.cpp_info.components["libpcre"].names["pkg_config"] = "libpcre"
            self.cpp_info.components["libpcre"].libs = [self._lib_name("pcre")]
            if not self.options.shared:
                self.cpp_info.components["libpcre"].defines.append("PCRE_STATIC=1")
            # pcreposix
            self.cpp_info.components["libpcreposix"].names["pkg_config"] = "libpcreposix"
            self.cpp_info.components["libpcreposix"].libs = [self._lib_name("pcreposix")]
            self.cpp_info.components["libpcreposix"].requires = ["libpcre"]
            # pcrecpp
            if self.options.build_pcrecpp:
                self.cpp_info.components["libpcrecpp"].names["pkg_config"] = "libpcrecpp"
                self.cpp_info.components["libpcrecpp"].libs = [self._lib_name("pcrecpp")]
                self.cpp_info.components["libpcrecpp"].requires = ["libpcre"]
        # pcre16
        if self.options.build_pcre_16:
            self.cpp_info.components["libpcre16"].names["pkg_config"] = "libpcre16"
            self.cpp_info.components["libpcre16"].libs = [self._lib_name("pcre16")]
            if not self.options.shared:
                self.cpp_info.components["libpcre16"].defines.append("PCRE_STATIC=1")
        # pcre32
        if self.options.build_pcre_32:
            self.cpp_info.components["libpcre32"].names["pkg_config"] = "libpcre32"
            self.cpp_info.components["libpcre32"].libs = [self._lib_name("pcre32")]
            if not self.options.shared:
                self.cpp_info.components["libpcre32"].defines.append("PCRE_STATIC=1")

        if self.options.build_pcregrep:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
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
