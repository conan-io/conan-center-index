import os

from conan import ConanFile, tools

required_conan_version = ">=1.33.0"

class NanosvgConan(ConanFile):
    name = "nanosvg"
    description = "NanoSVG is a simple stupid single-header-file SVG parser."
    license = "Zlib"
    topics = ("nanosvg", "svg", "parser", "header-only")
    homepage = "https://github.com/memononen/nanosvg"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "nanosvg"), src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "nanosvg"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
