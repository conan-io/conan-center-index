from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class LibmodplugConan(ConanFile):
    name = "libmodplug"
    description = "libmodplug - the library which was part of the Modplug-xmms project"
    topics = ("conan", "libmodplug", "auduo", "multimedia", "sound", "music", "mod", "mod music",
              "tracket music")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://modplug-xmms.sourceforge.net"
    license = "Unlicense"  # public domain

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
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

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libmodplug"
        self.cpp_info.libs = ["modplug"]
        self.cpp_info.includedirs.append(os.path.join("include", "libmodplug"))
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m"])
        if not self.options.shared:
            self.cpp_info.defines.append("MODPLUG_STATIC")
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.extend([stdcpp_library])
