import functools
import os

from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"


class FbClientConan(ConanFile):
    name = "fbclient"
    description = (
        "Firebird is a relational database offering many ANSI SQL standard "
        "features that runs on Linux, Windows, MacOS and a variety of Unix "
        "platforms."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.firebirdsql.org/"
    topics = "sql", "database", "db"
    license = "LicenseRef-IDPL.txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package_multi"
    # NOTE: The cpp files are from epp files pre-processed using the gpre tool
    #       See https://github.com/conan-io/conan-center-index/issues/9307
    exports_sources = "CMakeLists.txt", "array.cpp", "blob.cpp"
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libtommath/1.2.0")
        self.requires("zlib/1.2.11")
        if self.settings.os == "Macos":
            self.requires("libiconv/1.16")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.get(**get_args, destination=root, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_fbclient_VERSION"] = self.version
        # HACK: CMAKE_SYSTEM_PROCESSOR is not defined for M1 builds and the
        #       Configure.cmake script depends on it being defined
        if self.settings.arch == "armv8" and self.settings.os == "Macos":
            cmake.definitions["CONAN_CMAKE_SYSTEM_PROCESSOR"] = "armv8"
        cmake.configure()
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        license = os.path.join(self._source_subfolder, "doc", "license")
        self.copy("IDPL.txt", "licenses", license)
        self.copy("README.license.usage.txt", "licenses", license)
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["fbclient"]
        self.cpp_info.requires = ["libtommath::libtommath", "zlib::zlib"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Mpr", "Ws2_32"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.requires.append("libiconv::libiconv")
            self.cpp_info.frameworks = ["Foundation", "Security"]
