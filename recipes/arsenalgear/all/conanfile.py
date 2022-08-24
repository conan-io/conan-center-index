from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import functools

required_conan_version = ">=1.45.0"

class ArsenalgearConan(ConanFile):
    name = "arsenalgear"
    description = "A library containing general purpose C++ utils."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JustWhit3/arsenalgear-cpp"
    topics = ("constants", "math", "operators", "stream")
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

    def requirements(self):
        self.requires("boost/1.79.0")
        if self.settings.os in ["Linux", "Macos"]:
            self.requires("exprtk/0.0.1")

    @property
    def _compiler_required_cpp17(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def validate(self):
        # In 1.2.2, arsenalgear doesn't support Visual Studio.
        if is_msvc(self):
            raise ConanInvalidConfiguration("{} doesn't support Visual Studio(yet)".format(self.name))

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 17)

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["arsenalgear"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
