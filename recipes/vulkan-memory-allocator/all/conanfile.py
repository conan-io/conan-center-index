import os

from conans import ConanFile, tools


class VulkanMemoryAllocatorConan(ConanFile):
    name = "vulkan-memory-allocator"
    license = "MIT"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Easy to integrate Vulkan memory allocation library."
    topics = ("vulkan", "memory-allocator", "graphics")
    requires = ("vulkan-headers/1.2.182")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("VulkanMemoryAllocator-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("vk_mem_alloc.h", src=os.path.join(self._source_subfolder, "src"), dst="include")
