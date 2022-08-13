from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47.0"


class LibBigWigConan(ConanFile):
    name = "libbigwig"
    description = "A C library for handling bigWig files"
    topics = ("bioinformatics", "bigwig", "bigbed")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpryan79/libBigWig"
    license = "MIT"
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_curl": [True, False],
        "with_zlibng": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_curl": True,
        "with_zlibng": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_c_standard(self):
        return 11

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/[>=7.83 <7.85]")
        if self.options.with_zlibng:
            self.requires("zlib-ng/2.0.6")
        else:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows not supported")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.with_zlibng:
            self.options["zlib-ng"].zlib_compat = True

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["WITH_CURL"] = self.options.with_curl
        self._cmake.definitions["WITH_ZLIBNG"] = self.options.with_zlibng

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.system_libs = ["m"]
        self.cpp_info.names["cmake_find_package"] = "libBigWig"
        self.cpp_info.names["cmake_find_package_multi"] = "libBigWig"
        self.cpp_info.libs = tools.collect_libs(self)
