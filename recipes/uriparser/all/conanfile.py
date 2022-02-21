from conans import CMake, ConanFile, tools
import os

required_conan_version = ">=1.36.0"


class UriparserConan(ConanFile):
    name = "uriparser"
    description = "Strictly RFC 3986 compliant URI parsing and handling library written in C89"
    topics = ("conan", "uriparser", "URI", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://uriparser.github.io/"

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

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["URIPARSER_BUILD_DOCS"] = False
        self._cmake.definitions["URIPARSER_BUILD_TESTS"] = False
        self._cmake.definitions["URIPARSER_BUILD_TOOLS"] = False
        self._cmake.definitions["URIPARSER_BUILD_CHAR"] = self.options.with_char
        self._cmake.definitions["URIPARSER_BUILD_WCHAR"] = self.options.with_wchar
        if self.settings.compiler in ["Visual Studio", "msvc"]:
            if self.settings.compiler == "Visual Studio":
                runtime = self.settings.compiler.runtime
            else:
                runtime = "{}{}".format(
                    "MT" if self.settings.compiler.runtime == "static" else "MD",
                    "d" if self.settings.compiler.runtime_type == "Debug" else "",
                )
            self._cmake.definitions["URIPARSER_MSVC_RUNTIME"] = "/{}".format(runtime)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "liburiparser")
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("URI_STATIC_BUILD")
        if not self.options.with_char:
            self.cpp_info.defines.append("URI_NO_ANSI")
        if not self.options.with_wchar:
            self.cpp_info.defines.append("URI_NO_UNICODE")

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "liburiparser"
