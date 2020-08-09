from conans import CMake, ConanFile, tools
import glob
import os


class NanodbcConan(ConanFile):
    name = "nanodbc"
    description = "A small C++ wrapper for the native C ODBC API"
    topics = ("conan", "nanodbc", "odbc", "database")
    license = "MIT"
    homepage = "https://github.com/nanodbc/nanodbc/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "async": [True, False],
        "unicode": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "async": True,
        "unicode": False,
        "with_boost": False,
    }
    generators = "cmake", "cmake_find_package"

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
            tools.check_min_cppstd(self, 14)

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.73.0")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.7")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("nanodbc-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NANODBC_DISABLE_ASYNC"] = not self.options.get_safe("async")
        self._cmake.definitions["NANODBC_ENABLE_UNICODE"] = self.options.unicode
        self._cmake.definitions["NANODBC_ENABLE_BOOST"] = self.options.with_boost
        self._cmake.definitions["NANODBC_DISABLE_LIBCXX"] = self.settings.get_safe("compiler.libcxx") != "libc++"

        self._cmake.definitions["NANODBC_DISABLE_INSTALL"] = False
        self._cmake.definitions["NANODBC_DISABLE_EXAMPLES"] = True
        self._cmake.definitions["NANODBC_DISABLE_TESTS"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["nanodbc"]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["odbc32"]
