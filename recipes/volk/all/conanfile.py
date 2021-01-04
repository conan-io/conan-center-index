from conans import ConanFile, CMake, tools
import os


class VolkConan(ConanFile):
    name = "volk"
    license = "MIT"
    homepage = "https://github.com/zeux/volk"
    url = "https://github.com/conan-io/conan-center-index"
    description = "volk is a meta-loader for Vulkan. It allows you to \
    dynamically load entrypoints required to use Vulkan without linking\
     to vulkan-1.dll or statically linking Vulkan loader. Additionally,\
      volk simplifies the use of Vulkan extensions by automatically\
       loading all associated entrypoints. Finally, volk enables\
        loading Vulkan entrypoints directly from the driver which \
        can increase performance by skipping loader dispatch \
        overhead."
    topics = ("Vulkan", "loader", "extension", "entrypoint", "graphics")
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
        tools.get(**self.conan_data["sources"][self.version])
        commithash, _ = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))
        os.rename("volk-{}".format(commithash), self._source_subfolder)

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
        self.cpp_info.libs = ["volk"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
