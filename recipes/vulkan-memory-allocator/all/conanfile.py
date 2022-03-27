from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class VulkanMemoryAllocatorConan(ConanFile):
    name = "vulkan-memory-allocator"
    license = "MIT"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Easy to integrate Vulkan memory allocation library."
    topics = ("vulkan", "memory-allocator", "graphics")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "11" if tools.Version(self.version) < "3.0.0" else "14"

    def requirements(self):
        self.requires("vulkan-headers/1.3.204.1")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        if tools.Version(self.version) < "3.0.0":
            include_dir = os.path.join(self._source_subfolder, "src")
        else:
            include_dir = os.path.join(self._source_subfolder, "include")
        self.copy("vk_mem_alloc.h", src=include_dir, dst="include")
