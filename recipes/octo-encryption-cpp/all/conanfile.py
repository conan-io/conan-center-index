from conans import ConanFile, CMake
from conan.tools.files import get, collect_libs


class OctoEncryptionCPPConan(ConanFile):
    name = "octo-encryption-cpp"
    version = "1.0.0"
    license = "MIT"
    url = "https://github.com/ofiriluz/octo-encryption-cpp"
    homepage = "https://github.com/ofiriluz/octo-encryption-cpp"
    description = "Octo encryption library"
    topics = ("logging", "cpp")
    author = "Ofir Iluz"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "build"

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def requirements(self):
        self.requires("catch2/3.1.0")
        self.requires("openssl/3.0.5")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.build(build_dir=self._build_subfolder)
        cmake.test(build_dir=self._build_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = CMake(self)
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
