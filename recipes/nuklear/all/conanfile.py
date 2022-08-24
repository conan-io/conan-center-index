import os

from conan import ConanFile, tools

class NuklearConan(ConanFile):
    name = "nuklear"
    description = "A single-header ANSI C immediate mode cross-platform GUI library."
    license = ["MIT", "Unlicense"]
    topics = ("conan", "nuklear", "gui", "header-only")
    homepage = "https://github.com/Immediate-Mode-UI/Nuklear"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "Nuklear-" + os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder, "src"))
        self.copy("nuklear.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
