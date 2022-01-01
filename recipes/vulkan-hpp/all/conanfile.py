from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.44.0"

class VulkanHppConan(ConanFile):
    name = "vulkan_hpp"
    homepage = "https://github.com/KhronosGroup/Vulkan-Hpp"
    description = "C++ wrappers to the Vulkan API"
    topics = ("Vulkan", "graphics", "games")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("vulkan-headers/{}".format(self.version))

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "4",
            "apple-clang": "9"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "vulkan"))
        self.copy("*LICENSE*", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "vulkan_hpp"
        self.cpp_info.names["cmake_find_package_multi"] = "vulkan_hpp"
