from conans import ConanFile, CMake, tools
import os


class StduuidConan(ConanFile):
    name = "stduuid"
    description = "A C++17 cross-platform implementation for UUIDs"
    topics = ("conan", "uuid", "guid")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mariusbancila/stduuid"
    license = "MIT"

    requires = "ms-gsl/2.0.0"

    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        root_dir = self._source_subfolder
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=root_dir)
        self.copy(pattern="uuid.h", dst="include", src=include_dir)

    def package_info(self):
        self.cpp_info.defines.append('ASIO_STANDALONE')
        if tools.os_info.is_linux:
            self.cpp_info.libs.append('pthread')

    def package_id(self):
        self.info.header_only()
