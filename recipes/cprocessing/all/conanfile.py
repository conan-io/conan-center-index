from conans import ConanFile, tools
from conans.tools import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.43.0"

class CProcessingConan(ConanFile):
    name = "cprocessing"
    description = "Processsing programming for C++ "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/maksmakuta/CProcessing"
    topics = ("processing", "opengl", "sketch")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
                "gcc": "9",
                "Visual Studio": "16.2",
                "msvc": "19.22",
                "clang": "10",
                "apple-clang": "11"
        }

    def requirements(self):
        self.requires("glfw/3.3.7")
        self.requires("glm/0.9.9.8")
        self.requires("glew/2.2.0")
        self.requires("stb/cci.20210910")
        self.requires("opengl/system")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 20)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler_version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} requires C++20. Your compiler is unknown. Assuming it supports C++20.".format(self.name))
        elif lazy_lt_semver(compiler_version, minimum_version):
            raise ConanInvalidConfiguration("{} requires some C++20 features,".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "lib", "PImage.h"),
            "stb/stb_image.h",
            "stb_image.h")

    def package(self):
        self.copy("*.h", "include", os.path.join(self._source_subfolder, "lib"))

        # Extract the License/s from README.md to a file
        tmp = tools.files.load(self, os.path.join(self._source_subfolder, "README.md"))
        license_contents = re.search("(## Author.*)", tmp, re.DOTALL)[1]
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE.md"), license_contents)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CProcessing")
        self.cpp_info.set_property("cmake_target_name", "CProcessing::CProcessing")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "CProcessing"
        self.cpp_info.filenames["cmake_find_package_multi"] = "CProcessing"
        self.cpp_info.names["cmake_find_package"] = "CProcessing"
        self.cpp_info.names["cmake_find_package_multi"] = "CProcessing"
