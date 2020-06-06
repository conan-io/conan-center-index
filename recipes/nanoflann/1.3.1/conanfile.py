from conans import ConanFile, tools
import os
import glob


class NanoflannConan(ConanFile):
    name = "nanoflann"
    description = """nanoflann is a C++11 header-only library for building KD-Trees
                    of datasets with different topologies: R2, R3 (point clouds),
                    SO(2) and SO(3) (2D and 3D rotation groups).
                    """
    topics = ("conan", "nanoflann", "nearest-neighbor", "kd-trees")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jlblancoc/nanoflann"
    license = "BSD"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "nanoflann"
        self.cpp_info.names["cmake_find_package_multi"] = "nanoflann"
