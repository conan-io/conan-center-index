from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class VolkConan(ConanFile):
    name = "volk"
    license = "MIT"
    homepage = "https://github.com/zeux/volk"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "volk is a meta-loader for Vulkan. It allows you to dynamically load "
        "entrypoints required to use Vulkan without linking to vulkan-1.dll or "
        "statically linking Vulkan loader. Additionally, volk simplifies the "
        "use of Vulkan extensions by automatically loading all associated "
        "entrypoints. Finally, volk enables loading Vulkan entrypoints "
        "directly from the driver which can increase performance by skipping "
        "loader dispatch overhead."
    )
    topics = ("vulkan", "loader", "extension", "entrypoint", "graphics")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("vulkan-headers/" + self.version)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["VOLK_INSTALL"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "volk")

        self.cpp_info.components["libvolk"].set_property("cmake_target_name", "volk::volk")
        self.cpp_info.components["libvolk"].libs = ["volk"]
        self.cpp_info.components["libvolk"].requires = ["vulkan-headers::vulkan-headers"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libvolk"].system_libs = ["dl"]

        self.cpp_info.components["volk_headers"].set_property("cmake_target_name", "volk::volk_headers")
        self.cpp_info.components["volk_headers"].libs = []
        self.cpp_info.components["volk_headers"].requires = ["vulkan-headers::vulkan-headers"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["volk_headers"].system_libs = ["dl"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["libvolk"].names["cmake_find_package"] = "volk"
        self.cpp_info.components["libvolk"].names["cmake_find_package_multi"] = "volk"
