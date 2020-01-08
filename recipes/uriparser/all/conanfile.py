from conans import CMake, ConanFile, tools
import os


class UriparserConan(ConanFile):
    name = "uriparser"
    description = "Strictly RFC 3986 compliant URI parsing and handling library written in C89"
    topics = ("conan", "uriparser", "URI", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://uriparser.github.io/"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_char": [True, False],
        "with_wchar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_char": True,
        "with_wchar": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["URIPARSER_BUILD_DOCS"] = False
        cmake.definitions["URIPARSER_BUILD_TESTS"] = False
        cmake.definitions["URIPARSER_BUILD_TOOLS"] = False
        cmake.definitions["URIPARSER_BUILD_CHAR"] = self.options.with_char
        cmake.definitions["URIPARSER_BUILD_WCHAR"] = self.options.with_wchar
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["URIPARSER_MSVC_RUNTIME"] = "/{}".format(self.settings.compiler.runtime)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        if not self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "include", "uriparser", "UriBase.h"),
                                  "__declspec(dllimport)",
                                  "")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["uriparser"]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include")]
        defines = []
        if not self.options.shared:
            defines.append("URI_STATIC_BUILD")
        if not self.options.with_char:
            defines.append("URI_NO_ANSI")
        if not self.options.with_wchar:
            defines.append("URI_NO_UNICODE")
        self.cpp_info.defines = defines

