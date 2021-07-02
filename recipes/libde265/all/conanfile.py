from conans import ConanFile, CMake, tools
import os


class Libde265Conan(ConanFile):
    name = "libde265"
    description = "Open h.265 video codec implementation."
    license = "LGPL-3.0-or-later"
    topics = ("conan", "libde265", "codec", "video", "h.265")
    homepage = "https://github.com/strukturag/libde265"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sse": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sse": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.sse

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch_data in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch_data)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["ENABLE_SDL"] = False
        self._cmake.definitions["DISABLE_SSE"] = not self.options.get_safe("sse", False)
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # FIXME: imported CMake target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "libde265"
        self.cpp_info.names["cmake_find_package_multi"] = "libde265"
        self.cpp_info.names["pkg_config"] = "libde265"
        self.cpp_info.libs = ["libde265"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBDE265_STATIC_BUILD"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
