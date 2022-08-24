from conans import ConanFile, tools
from conans.tools import Version
import os

required_conan_version = ">=1.43.0"

class SophusConan(ConanFile):
    name = "sophus"
    description = "C++ implementation of Lie Groups using Eigen."
    topics = ("conan", "eigen", "numerical", "math")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://strasdat.github.io/Sophus/"
    license = "MIT"
    no_copy_source = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_fmt": [True, False],
    }
    default_options = {
        "with_fmt": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name.capitalize() + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("eigen/3.4.0")
        if self.options.with_fmt and Version(self.version) >= Version("22.04.1"):
            self.requires("fmt/8.1.1")

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.hpp", src=os.path.join(self._source_subfolder, "sophus"), dst=os.path.join("include", "sophus"), keep_path=False)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sophus")
        self.cpp_info.set_property("cmake_target_name", "Sophus::Sophus")
        self.cpp_info.set_property("pkg_config_name", "sophus")

        if not self.options.with_fmt:
            self.cpp_info.defines.append("SOPHUS_USE_BASIC_LOGGING=1")

        # TODO: to remove in conan v2 once cmake_find_package* generator removed
        self.cpp_info.names["cmake_find_package"] = "Sophus"
        self.cpp_info.names["cmake_find_package_multi"] = "Sophus"
