import os

from conans import ConanFile, tools


class VulkanMemoryAllocatorConan(ConanFile):
    name = "vulkan-memory-allocator"
    license = "MIT"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Easy to integrate Vulkan memory allocation library."
    topics = ("vulkan", "memory-allocator", "graphics")
    requires = ("vulkan-headers/[>=1.0]")
    no_copy_source = True
    # No settings/options are necessary, this is header only

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        version = os.path.basename(url).replace(".zip", "")
        if version.startswith('v'):
            version = version[1:]
        extracted_dir = "VulkanMemoryAllocator-" + version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        # This is a header only
        pass

    def package(self):
        self.copy("LICENSE.txt",
                  src=os.path.join(self.source_folder,
                                   self._source_subfolder),
                  dst="licenses")
        self.copy("vk_mem_alloc.h",
                  src=os.path.join(self.source_folder,
                                   self._source_subfolder,
                                   "src"),
                  dst="include")
