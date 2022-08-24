from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class AstroInformaticsSO3(ConanFile):
    name = "astro-informatics-so3"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/so3"
    description = "Fast and accurate Wigner transforms"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("physics", "astrophysics", "radio interferometry")

    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("fftw/3.3.9")
        self.requires("ssht/1.3.7")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "Visual Studio not supported, since SO3 requires C99 support for complex numbers"
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.definitions["conan_deps"] = False
            self._cmake.definitions["BUILD_TESTING"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self.cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["astro-informatics-so3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
