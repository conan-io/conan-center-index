from conans import ConanFile, CMake, tools
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
        "with_bzip2": [True, False],
        "with_zlib": [True, False],
        "with_jit": [True, False],
        "build_pcrecpp": [True, False],
        "build_pcregrep": [True, False],
        "with_utf": [True, False],
        "with_unicode_properties": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bzip2": True,
        "with_zlib": True,
        "with_jit": False,
        "build_pcrecpp": False,
        "build_pcregrep": False,
        "with_utf": False,
        "with_unicode_properties": False
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
        if not self.options.build_pcrecpp:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if self.options.with_unicode_properties:
            self.options.with_utf = True

    def requirements(self):
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_zlib:
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
        self._cmake.definitions["PCRE_BUILD_PCREGREP"] = self.options.build_pcregrep
        self._cmake.definitions["PCRE_BUILD_PCRECPP"] = self.options.build_pcrecpp
        self._cmake.definitions["PCRE_SUPPORT_LIBZ"] = self.options.with_zlib
        self._cmake.definitions["PCRE_SUPPORT_LIBBZ2"] = self.options.with_bzip2
        self._cmake.definitions["PCRE_SUPPORT_JIT"] = self.options.with_jit
        self._cmake.definitions["PCRE_SUPPORT_UTF"] = self.options.with_utf
        self._cmake.definitions["PCRE_SUPPORT_UNICODE_PROPERTIES"] = self.options.with_unicode_properties
        self._cmake.definitions["PCRE_SUPPORT_LIBREADLINE"] = False
        self._cmake.definitions["PCRE_SUPPORT_LIBEDIT"] = False
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
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            self.cpp_info.libs = ["pcreposixd", "pcred"]
        else:
            self.cpp_info.libs = ["pcreposix", "pcre"]
        if not self.options.shared:
            self.cpp_info.defines.append("PCRE_STATIC=1")
        self.cpp_info.names["pkg_config"] = "libpcre"

        self.cpp_info.names["cmake_find_package"] = "PCRE"
        self.cpp_info.names["cmake_find_package_multi"] = "PCRE"
