import os
import glob
from conans import ConanFile, tools, CMake


class RTTRConan(ConanFile):
    name = "rttr"
    description = "Run Time Type Reflection library"
    topics = ("conan", "reflection", "rttr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rttrorg/rttr"
    license = "MIT"

    exports_sources = "CMakeLists.txt", "patches/*.patch",
    generators = "cmake",

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtti": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_WITH_RTTI"] = self.options.with_rtti
        self._cmake.definitions["BUILD_PACKAGE"] = False
        self._cmake.definitions["BUILD_RTTR_DYNAMIC"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        for pdb in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.remove(pdb)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "rttr"
        self.cpp_info.filenames["cmake_find_package_multi"] = "rttr"
        self.cpp_info.names["cmake_find_package"] = "RTTR"
        self.cpp_info.names["cmake_find_package_multi"] = "RTTR"
        cmake_target = "Core" if self.options.shared else "Core_Lib"
        self.cpp_info.components["_rttr"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_rttr"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_rttr"].libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.components["_rttr"].system_libs = ["dl", "pthread"]
        if self.options.shared:
            self.cpp_info.components["_rttr"].defines = ["RTTR_DLL"]
