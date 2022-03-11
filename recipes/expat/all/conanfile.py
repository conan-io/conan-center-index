from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class ExpatConan(ConanFile):
    name = "expat"
    description = "Fast streaming XML parser written in C."
    topics = ("expat", "xml", "parsing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libexpat/libexpat"
    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "char_type": ["char", "wchar_t", "ushort"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "char_type": "char",
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
        if tools.Version(self.version) < "2.2.8":
            del self.options.char_type

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) < "2.2.8":
            self._cmake.definitions["BUILD_doc"] = "Off"
            self._cmake.definitions["BUILD_examples"] = "Off"
            self._cmake.definitions["BUILD_shared"] = self.options.shared
            self._cmake.definitions["BUILD_tests"] = "Off"
            self._cmake.definitions["BUILD_tools"] = "Off"
        else:
            # These options were renamed in 2.2.8 to be more consistent
            self._cmake.definitions["EXPAT_BUILD_DOCS"] = "Off"
            self._cmake.definitions["EXPAT_BUILD_EXAMPLES"] = "Off"
            self._cmake.definitions["EXPAT_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["EXPAT_BUILD_TESTS"] = "Off"
            self._cmake.definitions["EXPAT_BUILD_TOOLS"] = "Off"
            # EXPAT_CHAR_TYPE was added in 2.2.8
            self._cmake.definitions["EXPAT_CHAR_TYPE"] = self.options.char_type
            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["EXPAT_MSVC_STATIC_CRT"] = "MT" in self.settings.compiler.runtime
        if tools.Version(self.version) >= "2.2.10":
            self._cmake.definitions["EXPAT_BUILD_PKGCONFIG"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "EXPAT")
        self.cpp_info.set_property("cmake_module_target_name", "EXPAT::EXPAT")
        self.cpp_info.set_property("cmake_file_name", "expat")
        self.cpp_info.set_property("cmake_target_name", "expat::expat")
        self.cpp_info.set_property("pkg_config_name", "expat")

        self.cpp_info.names["cmake_find_package"] = "EXPAT"
        self.cpp_info.names["cmake_find_package_multi"] = "expat"

        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]
        if self.options.get_safe("char_type") in ("wchar_t", "ushort"):
            self.cpp_info.defines.append("XML_UNICODE")
        elif self.options.get_safe("char_type") == "wchar_t":
            self.cpp_info.defines.append("XML_UNICODE_WCHAR_T")
