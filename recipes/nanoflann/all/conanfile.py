import os
from conans import ConanFile, tools


class NanoflannConan(ConanFile):
    name = "nanoflann"
    description = """nanoflann is a C++11 header-only library for building KD-Trees
                    of datasets with different topologies: R2, R3 (point clouds),
                    SO(2) and SO(3) (2D and 3D rotation groups).
                    """
    topics = ("conan", "nanoflann", "nearest-neighbor", "kd-trees")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jlblancoc/nanoflann"
    license = "BSD-2-Clause"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()
