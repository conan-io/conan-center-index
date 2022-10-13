from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class CubicInterpolationConan(ConanFile):
    name = "cubicinterpolation"
    homepage = "https://github.com/MaxSac/cubic_interpolation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Leightweight interpolation library based on boost and eigen."
    topics = ("interpolation", "splines", "cubic", "bicubic", "boost", "eigen3")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        # TODO: update boost dependency as soon as issue #11207 is fixed
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    @property
    def _required_boost_components(self):
        return ["filesystem", "math", "serialization"]

    def validate(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("{0} requires non header-only boost with these components: {1}".format(self.name, ", ".join(self._required_boost_components)))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False
        )
        if not minimum_version:
            self.output.warn(
                "CubicInterpolation requires C++14. Your compiler is unknown. Assuming it supports C++14."
            )
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "CubicInterpolation requires C++14, which your compiler does not support."
            )

        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("cubicinterpolation shared is not supported with Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLE"] = False
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CubicInterpolation")
        self.cpp_info.set_property("cmake_target_name", "CubicInterpolation::CubicInterpolation")
        self.cpp_info.libs = ["CubicInterpolation"]
        self.cpp_info.requires = ["boost::headers", "boost::filesystem", "boost::math", "boost::serialization", "eigen::eigen"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CubicInterpolation"
        self.cpp_info.names["cmake_find_package_multi"] = "CubicInterpolation"
