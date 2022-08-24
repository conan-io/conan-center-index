import functools
from conans import ConanFile, CMake, tools
from conans.tools import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.43.0"

class LibslzConan(ConanFile):
    name = "libslz"
    description = "Simple, modern libpng alternative "
    topics = ("zlib", "compression",)
    license = "X11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.libslz.org/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("{}/{} does not support Visual Studio.".format(self.name, self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["slz"]
