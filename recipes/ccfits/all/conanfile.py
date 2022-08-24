from conan import ConanFile, tools
from conan.tools.cmake import CMake

required_conan_version = ">=1.36.0"


class CcfitsConan(ConanFile):
    name = "ccfits"
    description = "CCfits is an object oriented interface to the cfitsio library."
    license = "ISC"
    topics = ("ccfits", "fits", "image", "nasa", "astronomy", "astrophysics", "space")
    homepage = "https://heasarc.gsfc.nasa.gov/fitsio/ccfits"
    url = "https://github.com/conan-io/conan-center-index"

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
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("cfitsio/4.0.0")

    def validate(self):
        if tools.Version(self.version) >= "2.6":
            if self.settings.compiler.get_safe("cppstd"):
                tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "CCfits")
        self.cpp_info.libs = ["CCfits"]

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "CCfits"
