from from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class QXlsxConan(ConanFile):
    name = "qxlsx"
    description = "Excel file(*.xlsx) reader/writer library using Qt 5 or 6."
    license = "MIT"
    topics = ("qxlsx", "excel", "xlsx")
    homepage = "https://github.com/QtExcel/QXlsx"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("qt/5.15.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QXlsx")
        self.cpp_info.set_property("cmake_target_name", "QXlsx::Core")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["qxlsx_core"].libs = ["QXlsx"]
        self.cpp_info.components["qxlsx_core"].includedirs = [os.path.join("include", "QXlsx")]
        self.cpp_info.components["qxlsx_core"].requires = ["qt::qtCore", "qt::qtGui"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "QXlsx"
        self.cpp_info.names["cmake_find_package_multi"] = "QXlsx"
        self.cpp_info.components["qxlsx_core"].names["cmake_find_package"] = "Core"
        self.cpp_info.components["qxlsx_core"].names["cmake_find_package_multi"] = "Core"
        self.cpp_info.components["qxlsx_core"].set_property("cmake_target_name", "QXlsx::Core")
