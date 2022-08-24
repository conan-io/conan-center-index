import os
from from conan import ConanFile, tools
from conans import CMake


class QtXlsxWriterConan(ConanFile):
    name = "qtxlsxwriter"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dbzhang800/QtXlsxWriter"
    description = ".xlsx file reader and writer for Qt5"
    topics = ("qtxlsxwriter", "excel", "xlsx", "conan-recipe")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["QT_ROOT"] = self.deps_cpp_info["qt"].rootpath.replace("\\", "/")
        self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("qt/5.15.2")

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url.rsplit("/", 1)[-1]
            tools.files.download(self, url, filename, sha256=source["sha256"])
        tools.files.unzip(self, os.path.join(self.source_folder, "v0.3.0.zip"), self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses")

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines = ["QTXLSX_STATIC"]
        self.cpp_info.libs = tools.files.collect_libs(self, self)
