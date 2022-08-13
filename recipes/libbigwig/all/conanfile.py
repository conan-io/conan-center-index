from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, get
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"


class LibBigWigConan(ConanFile):
    name = "libbigwig"
    description = "A C library for handling bigWig files"
    topics = ("bioinformatics", "bigwig", "bigbed")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dpryan79/libBigWig"
    license = "MIT"
    settings = "arch", "build_type", "compiler", "os"

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ENABLE_TESTING"] = False
        tc.variables["WITH_CURL"] = self.options.with_curl
        tc.variables["WITH_ZLIBNG"] = self.options.with_zlibng

        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/[>=7.83 <7.85]")
        if self.options.with_zlibng:
            self.requires("zlib-ng/2.0.6")
        else:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows not supported")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        if self.options.with_zlibng:
            self.options["zlib-ng"].zlib_compat = True

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.system_libs = ["m"]
        self.cpp_info.names["cmake_find_package"] = "libBigWig"
        self.cpp_info.names["cmake_find_package_multi"] = "libBigWig"
        self.cpp_info.libs = collect_libs(self)
