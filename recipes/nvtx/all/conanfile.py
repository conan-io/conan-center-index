from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"

class NVTXConan(ConanFile):
    name = "nvtx"
    description = "The NVIDIA Tools Extension SDK (NVTX) is a C-based API for annotating events, code ranges, and resources in your applications."
    homepage = "https://github.com/NVIDIA/NVTX"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("profiler", "nvidia", "nsight")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self._source_subfolder, "c", "include"))

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
