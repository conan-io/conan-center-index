import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class SdbusCppConan(ConanFile):
    name = "sdbus-cpp"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kistler-Group/sdbus-cpp"
    description = "High-level C++ D-Bus library for Linux designed" \
                  " to provide easy-to-use yet powerful API in modern C++"
    topics = ("dbus", "sd-bus", "sdbus-c++", "sdbus-cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_code_gen": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_code_gen": False,
    }
    exports_sources = ("CMakeLists.txt", "patches/**")
    generators = ("cmake", "pkg_config")
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "6",
        }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        if self.options.with_code_gen:
            self.build_requires("expat/2.4.8")

    def requirements(self):
        self.requires("libsystemd/251.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_CODE_GEN"] = self.options.with_code_gen
        self._cmake.definitions["BUILD_DOC"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_LIBSYSTEMD"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SDBusCpp"
        self.cpp_info.names["cmake_find_package_multi"] = "SDBusCpp"
        self.cpp_info.filenames["cmake_find_package"] = "sdbus-c++"
        self.cpp_info.filenames["cmake_find_package_multi"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].libs = ["sdbus-c++"]
        self.cpp_info.components["sdbus-c++"].requires.append("libsystemd::libsystemd")
        self.cpp_info.components["sdbus-c++"].names["cmake_find_package"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].names["cmake_find_package_multi"] = "sdbus-c++"
        self.cpp_info.components["sdbus-c++"].names["pkg_config"] = "sdbus-c++"
        if self.options.with_code_gen:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
