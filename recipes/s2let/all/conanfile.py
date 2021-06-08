from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class S2let(ConanFile):
    name = "s2let"
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/astro-informatics/s2let"
    description = "Fast wavelets on the sphere"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("physics", "astrophysics", "radio interferometry")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    requires = "astro-informatics-so3/1.3.4", "cfitsio/3.490"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "S2LET requires C99 support for complex numbers."
            )

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    @property
    def _cmake(self):
        if not hasattr(self, "_cmake_instance"):
            self._cmake_instance = CMake(self)
            self._cmake_instance.definitions["BUILD_TESTING"] = False
            self._cmake_instance.definitions["cfitsio"] = True
            self._cmake_instance.configure(build_folder=self._build_subfolder)
        return self._cmake_instance

    def build(self):
        self._cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self._cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["s2let"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
