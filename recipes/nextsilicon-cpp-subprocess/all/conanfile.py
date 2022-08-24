from conan import ConanFile, tools


class CppSubprocess(ConanFile):
    name = "nextsilicon-cpp-subprocess"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nextsilicon/cpp-subprocess"
    topics = ("subprocess", "os", "fork")
    description = ("Subprocessing with modern C++, "
                   "The only goal was to develop something that is as close as"
                   "python subprocess module in dealing with processes.")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    _source_subfolder = 'cpp-subprocess'

    def source(self):
        tools.files.get(self, **self.conan_data['sources'][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("subprocess.hpp", dst="include/cpp-subprocess", src=self._source_subfolder)
        self.copy("LICENSE.MIT", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
