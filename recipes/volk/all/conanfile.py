from conans import ConanFile, CMake, tools


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
    topics = ("Vulkan", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    no_copy_source = True

    def source(self):
        self.run("git clone https://github.com/zeux/volk.git")
        self.run("cd volk/ && git checkout %s" % self.version)

    def package(self):
        self.copy("*volk.h", dst="include")
        self.copy("*volk.c", dst="include")
        self.copy("*LICENSE.md", dst="licenses")

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["dl"])

    def package_id(self):
        self.info.header_only()

