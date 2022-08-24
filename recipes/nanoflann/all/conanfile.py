from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class NanoflannConan(ConanFile):
    name = "nanoflann"
    description = """nanoflann is a C++11 header-only library for building KD-Trees
                    of datasets with different topologies: R2, R3 (point clouds),
                    SO(2) and SO(3) (2D and 3D rotation groups).
                    """
    topics = ("nanoflann", "nearest-neighbor", "kd-trees")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jlblancoc/nanoflann"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nanoflann")
        self.cpp_info.set_property("cmake_target_name", "nanoflann::nanoflann")
        self.cpp_info.set_property("pkg_config_name", "nanoflann")
