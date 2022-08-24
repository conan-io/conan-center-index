from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


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
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")
        if self.settings.compiler == "gcc":
            if tools.scm.Version(self.settings.compiler.version) < "6":
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        self.requires("libfuse/3.10.5")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fusepp"]
        # TODO: Remove after Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "fusepp"
        self.cpp_info.names["cmake_find_package_multi"] = "fusepp"

        self.cpp_info.set_property("cmake_file_name", "fusepp")
        self.cpp_info.set_property("cmake_target_name", "fusepp")
