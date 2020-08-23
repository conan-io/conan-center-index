from conans import ConanFile, tools
import os


class OpenclHeadersConan(ConanFile):
    name = "opencl-headers"
    description = "C language headers for the OpenCL API"
    license = "Apache-2.0"
    topics = ("conan", "opencl-headers", "opencl", "header-only", "api-headers")
    homepage = "https://github.com/KhronosGroup/OpenCL-Headers"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("OpenCL-Headers-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst=os.path.join("include", "CL"), src=os.path.join(self._source_subfolder, "CL"))
