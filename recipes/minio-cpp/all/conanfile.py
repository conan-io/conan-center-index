from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class MinioCppConan(ConanFile):
    name = "minio-cpp"
    description = "MinIO C++ Client SDK for Amazon S3 Compatible Cloud Storage"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/minio/minio-cpp"
    topics = ("minio", "s3", "storage")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("curlpp/0.8.1.cci.20240530", transitive_headers=True)
        self.requires("inih/58")
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pugixml/1.14")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("curlpp", "cmake_file_name", "unofficial-curlpp")
        deps.set_property("curlpp", "cmake_target_name", "unofficial::curlpp::curlpp")
        deps.set_property("inih", "cmake_file_name", "unofficial-inih")
        deps.set_property("inih", "cmake_target_name", "unofficial::inih::inireader")
        deps.set_property("pugixml", "cmake_target_name", "pugixml")
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["miniocpp"]

        self.cpp_info.set_property("cmake_file_name", "miniocpp")
        self.cpp_info.set_property("cmake_target_name", "miniocpp::miniocpp")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("wsock32")
            self.cpp_info.system_libs.append("ws2_32")
