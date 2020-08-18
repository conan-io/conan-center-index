from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class ThreeFDConan(ConanFile):
    name = "3fd"
    description = "C++ Framework For Fast Development: OOP wrappers and helpers for OpenCL, SQLite, Microsoft RPC API (DCE), Windows Web Services API (SOAP), Extensible Storage Engine (ESENT) and Service Broker (SQL Server)."
    topics = ("conan", "3fd", "opencl", "isam", "esent", "sqlite", "wrapper")
    license = "MS-PL"
    homepage = "https://github.com/faburaya/3fd"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    _compiler_cppstd17 = {
        "gcc": 7,
        "clang": 4,
        "Visual Studio": 16,
    }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        compiler_version_required = self._compiler_cppstd17.get(str(self.settings.compiler))
        if compiler_version_required:
            if tools.Version(self.settings.compiler.version) < compiler_version_required:
                raise ConanInvalidConfiguration("3fd requires a compiler supporting c++17")

    def requirements(self):
        self.requires("nanodbc/cci.20200807")
        self.requires("sqlite3/3.32.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("3fd-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.rmdir(os.path.join(self._source_subfolder, "nanodb"))
        tools.rmdir(os.path.join(self._source_subfolder, "sqlite"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["_base"].libs = ["3fd-core", "3fd-utils"]
        self.cpp_info.components["sqlite"].libs = ["3fd-sqlite"]
        self.cpp_info.components["sqlite"].requires = ["_base", "sqlite3::sqlite3"]
        self.cpp_info.components["broker"].libs = ["3fd-broker"]
        self.cpp_info.components["broker"].requires = ["_base", "nanodbc::nanodbc"]
        self.cpp_info.components["opencl"].libs = ["3fd-opencl"]
        self.cpp_info.components["opencl"].requires = ["_base"]
