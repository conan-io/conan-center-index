import os, glob, shutil
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conans import ConanFile, tools


class QtXlsxWriterConan(ConanFile):
    name = "qtxlsxwriter"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dbzhang800/QtXlsxWriter"
    description = "A library that can read and write Excel files"
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

    generators = "CMakeDeps"
    exports_sources = [
        "CMakeLists.txt",
        os.path.join("cmake", "*"),
        os.path.join("patches", "*"),
        os.path.join("src", "CMakeLists.txt")
    ]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("qt/5.15.2")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PROJECT_VERSION"] = "0.3.0"
        tc.variables["PROJECT_VERSION_MAJOR"] = "0"
        tc.variables["PROJECT_VERSION_MINOR"] = "3"
        tc.variables["PROJECT_VERSION_PATCH"] = "0"
        tc.variables["QT_ROOT"] = self.deps_cpp_info["qt"].rootpath.replace("\\", "/")
        tc.generate()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("QtXlsxWriter-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)
        shutil.copy("CMakeLists.txt", os.path.join(self._source_subfolder, "CMakeLists.txt"))
        shutil.copy(os.path.join("src", "CMakeLists.txt"), os.path.join(self._source_subfolder, "src", "CMakeLists.txt"))

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines = ["QTXLSX_STATIC"]
        self.cpp_info.libs = tools.collect_libs(self)
