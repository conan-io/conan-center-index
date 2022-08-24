from conans import ConanFile, tools
import os


class TcbSpanConan(ConanFile):
    name = "tcb-span"
    description = "Implementation of C++20's std::span for older C++ standards"
    topics = ("conan", "span", "header-only", "tcb-span")
    homepage = "https://github.com/tcbrindle/span"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    settings = "compiler"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE*.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
