import os
import glob
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

class OisConan(ConanFile):
    name = "ois"
    description = "Object oriented Input System."
    topics = ("conan", "ois", "input" )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wgois/OIS"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "OIS-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OIS_BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["OIS_BUILD_DEMOS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.names["pkg_config"] = "OIS"
        self.cpp_info.names["cmake_find_package"] = "OIS"
        self.cpp_info.names["cmake_find_package_multi"] = "OIS"

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["Foundation", "Cocoa", "IOKit"]
        elif self.settings.os == "Windows":
            self.cpp_info.defines = ["OIS_WIN32_XINPUT_SUPPORT"]
            self.cpp_info.system_libs = ["dinput8", "dxguid"]
            if self.options.shared:
                self.cpp_info.defines.append("OIS_DYNAMIC_LIB")
