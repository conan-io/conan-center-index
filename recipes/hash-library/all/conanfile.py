from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import apply_conandata_patches, get
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.52.0"


class HashLibraryConan(ConanFile):
    name = "hash-library"
    description = "Portable C++ hashing library"
    homepage = "https://create.stephan-brumme.com/hash-library/"
    topics = ("hash", "digest", "hmac", "checksum", "crc32", "md5", "sha1", "sha2", "sha256", "sha3", "keccak")
    license = "Zlib"
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
    generators = "CMakeToolchain"
    exports_sources = ["CMakeLists.txt", "patches/*"]


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["hash-library"]

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("hash-library does not support shared builds on Windows.")
