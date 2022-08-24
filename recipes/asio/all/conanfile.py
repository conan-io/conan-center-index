from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class Asio(ConanFile):
    name = "asio"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://think-async.com/Asio"
    description = "Asio is a cross-platform C++ library for network and low-level I/O"
    topics = ("conan", "asio", "network", "io", "low-level")
    settings = "os"
    license = "BSL-1.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        root_dir = os.path.join(self._source_subfolder, self.name)
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=root_dir)
        self.copy(pattern="*.hpp", dst="include", src=include_dir)
        self.copy(pattern="*.ipp", dst="include", src=include_dir)

    def package_info(self):
        self.cpp_info.defines.append("ASIO_STANDALONE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
