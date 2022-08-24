import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibxlsxwriterConan(ConanFile):
    name = "libxlsxwriter"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jmcnamara/libxlsxwriter"
    topics = ("conan", "Excel", "XLSX")
    description = "A C library for creating Excel XLSX files"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tmpfile": [True, False],
        "md5": [False, "openwall", "openssl"],
        "fmemopen": [True, False],
        "dtoa": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tmpfile": False,
        "md5": "openwall",
        "fmemopen": False,
        "dtoa": False,
    }
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.fmemopen

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if tools.scm.Version(self, self.version) <= "1.0.5" and self.options.md5 == "openssl":
            raise ConanInvalidConfiguration("{0}:md5=openssl is not suppported in {0}/{1}".format(self.name, self.version))

    def requirements(self):
        self.requires("minizip/1.2.12")
        self.requires("zlib/1.2.12")
        if self.options.md5 == "openssl":
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["USE_STATIC_MSVC_RUNTIME"] = (self.settings.os == "Windows" and "MT" in str(self.settings.compiler.runtime))
        self._cmake.definitions["USE_SYSTEM_MINIZIP"] = True
        self._cmake.definitions["USE_STANDARD_TMPFILE"] = self.options.tmpfile

        if self.options.md5 == False:
            self._cmake.definitions["USE_NO_MD5"] = True
        elif self.options.md5 == "openssl":
            self._cmake.definitions["USE_OPENSSL_MD5"] = True

        self._cmake.definitions["USE_FMEMOPEN"] = self.options.get_safe("fmemopen", False)
        self._cmake.definitions["USE_DTOA_LIBRARY"] = self.options.dtoa

        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("License.txt", src=self._source_subfolder, dst="licenses")
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.pc")

    def package_info(self):
        self.cpp_info.libs = ["xlsxwriter"]
