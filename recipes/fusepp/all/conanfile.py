from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class FuseppConan(ConanFile):
    name = "fusepp"
    description = "A simple C++ wrapper for the FUSE filesystem."
    license = "MIT"
    topics = ("fuse", "fusepp", "wrapper", "filesystem")
    homepage = "https://github.com/jachappell/Fusepp"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    exports_sources = "CMakeLists.txt"

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")
        if self.settings.compiler == "gcc":
            if tools.Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration("gcc < 6 is unsupported")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("libfuse/3.10.5")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("Fuse*.h", dst="include", src=self._source_subfolder)
        self.copy("Fuse.cpp", dst="include", src=self._source_subfolder)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
