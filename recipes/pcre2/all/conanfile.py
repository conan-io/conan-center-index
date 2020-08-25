from conans import ConanFile, CMake, tools
import os


class PCREConan(ConanFile):
    name = "pcre2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.pcre.org/"
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
        "build_pcre2_8": [True, False],
        "build_pcre2_16": [True, False],
        "build_pcre2_32": [True, False],
        "support_jit": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'with_bzip2': True,
        'build_pcre2_8': True,
        'build_pcre2_16': True,
        'build_pcre2_32': True,
        'support_jit': False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
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
        def library_name(library):
            if self.settings.build_type == "Debug" and self.settings.os == "Windows":
                library += "d"
            if self.settings.compiler == "gcc" and self.settings.os == "Windows" and self.options.shared:
                library += ".dll"
            return library

        # May need components for
        # ./lib/pkgconfig/libpcre2-32.pc
        # ./lib/pkgconfig/libpcre2-8.pc
        # ./lib/pkgconfig/libpcre2-posix.pc
        # ./lib/pkgconfig/libpcre2-16.pc

        self.cpp_info.names["pkg_config"] = "libpcre2"
        self.cpp_info.libs = [library_name("pcre2-posix")]
        if self.options.build_pcre2_8:
            self.cpp_info.libs.append(library_name("pcre2-8"))
        if self.options.build_pcre2_16:
            self.cpp_info.libs.append(library_name("pcre2-16"))
        if self.options.build_pcre2_32:
            self.cpp_info.libs.append(library_name("pcre2-32"))
        if not self.options.shared:
            self.cpp_info.defines.append("PCRE2_STATIC")
