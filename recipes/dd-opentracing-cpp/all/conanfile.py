from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DatadogOpenTracingConan(ConanFile):
    name = "dd-opentracing-cpp"
    description = (
        "Monitoring service for cloud-scale applications based on OpenTracing "
    )
    license = "Apache-2.0"
    topics = ("instrumentration", "monitoring", "security", "tracing")
    homepage = "https://github.com/DataDog/dd-opentracing-cpp"
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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15",
            "clang": "4.0",
            "apple-clang": "7",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_PLUGIN"] = False
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("opentracing-cpp/1.6.0")
        self.requires("zlib/1.2.13")
        self.requires("libcurl/7.85.0")
        self.requires("msgpack/3.3.0")
        self.requires("nlohmann_json/3.11.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    "Datadog-opentracing requires C++14, which your compiler does not support."
                )
        else:
            self.output.warn(
                "Datadog-opentracing requires C++14. Your compiler is unknown. Assuming it supports C++14."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["dd_opentracing"].libs = ["dd_opentracing"]
        self.cpp_info.components["dd_opentracing"].defines.append(
            "DD_OPENTRACING_SHARED" if self.options.shared else "DD_OPENTRACING_STATIC"
        )
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["dd_opentracing"].system_libs.append("pthread")

        self.cpp_info.names["cmake_find_package"] = "DataDogOpenTracing"
        self.cpp_info.names["cmake_find_package_multi"] = "DataDogOpenTracing"
        target_suffix = "" if self.options.shared else "-static"
        self.cpp_info.components["dd_opentracing"].names["cmake_find_package"] = (
            "dd_opentracing" + target_suffix
        )
        self.cpp_info.components["dd_opentracing"].names["cmake_find_package_multi"] = (
            "dd_opentracing" + target_suffix
        )
        self.cpp_info.components["dd_opentracing"].requires = [
            "opentracing-cpp::opentracing-cpp",
            "zlib::zlib",
            "libcurl::libcurl",
            "msgpack::msgpack",
            "nlohmann_json::nlohmann_json",
        ]
