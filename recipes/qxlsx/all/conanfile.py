import os
from conans import CMake, ConanFile, tools


class QXlsxConan(ConanFile):
    name = "qxlsx"
    description = "Excel file(*.xlsx) reader/writer library using Qt 5 or 6."
    license = "MIT"
    topics = ("qxlsx", "excel", "xlsx")
    homepage = "https://github.com/QtExcel/QXlsx"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/*"

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

    def requirements(self):
        self.requires("qt/5.15.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIB"] = self.options.shared
        self._cmake.definitions["QXLSX_PARENTPATH"] = os.path.join(self._source_subfolder, "QXlsx")
        self._cmake.definitions["QXLSX_HEADERPATH"] = os.path.join(self._source_subfolder, "QXlsx", "header")
        self._cmake.definitions["QXLSX_SOURCEPATH"] = os.path.join(self._source_subfolder, "QXlsx", "source")
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "QXlsx")
        self.cpp_info.names["cmake_find_package"] = "QXlsx"
        self.cpp_info.names["cmake_find_package_multi"] = "QXlsx"
