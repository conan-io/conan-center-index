from conans import ConanFile, tools
import glob
import os


class DtlConan(ConanFile):
    name = "dtl"
    description = "diff template library written by C++"
    topics = ("diff", "library", "algorithm")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cubicdaiya/dtl"
    license = "BSD"
    no_copy_source = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        src_dir = glob.glob(f"{self.name}-*/")[0]
        os.rename(src_dir, "dtl")

    def package(self):
        self.copy("dtl/*", dst="include", src="dtl")
        self.copy(pattern="COPYING", dst="licenses", src="dtl")

    def package_id(self):
        self.info.header_only()
