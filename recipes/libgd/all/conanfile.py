from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class LibgdConan(ConanFile):
    name = "libgd"
    license = "BSD-like"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GD is an open source code library for the dynamic "
                   "creation of images by programmers.")
    topics = ("images", "graphics")
    homepage = "https://libgd.github.io"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt", "patches/**"
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

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        tools.replace_in_file(cmakelists,
                              "SET(CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")",
                              "LIST(APPEND CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "RUNTIME DESTINATION bin",
                              "RUNTIME DESTINATION bin BUNDLE DESTINATION bin")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        if tools.Version(self.version) >= "2.3.0":
            self._cmake.definitions["ENABLE_GD_FORMATS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses",
                  ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"]= "gdlib"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("BGD_NONDLL")
            self.cpp_info.defines.append("BGDWIN32")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
