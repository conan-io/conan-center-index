from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class CppgraphqlgenConan(ConanFile):
    name = "cppgraphqlgen"
    description = "C++ GraphQL schema service generator."
    license = "MIT"
    topics = ("conan", "cppgraphqlgen", "graphql")
    homepage = "https://github.com/microsoft/cppgraphqlgen"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rapidjson": [True, False],
        "schemagen": [True, False],
        "clientgen": [True, False],

    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rapidjson": True,
        "schemagen": True,
        "clientgen": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("taocpp-pegtl/3.2.0")
        if self.options.with_rapidjson:
            self.requires("rapidjson/cci.20200410")
        if self.options.schemagen or self.options.clientgen:
            self.requires("boost/1.76.0")

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "8",
            "clang": "6.0",
            "apple-clang": "10"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

        if self.options.schemagen or self.options.clientgen:
            if self.options["boost"].header_only or self.options["boost"].without_program_options:
                raise ConanInvalidConfiguration("{} requires non header-only boost with program_options component".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GRAPHQL_BUILD_SCHEMAGEN"] = self.options.schemagen
        self._cmake.definitions["GRAPHQL_UPDATE_SAMPLES"] = False
        self._cmake.definitions["GRAPHQL_BUILD_CLIENTGEN"] = self.options.clientgen
        self._cmake.definitions["GRAPHQL_UPDATE_VERSION"] = True
        self._cmake.definitions["GRAPHQL_USE_RAPIDJSON"] = self.options.with_rapidjson
        self._cmake.definitions["GRAPHQL_BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cppgraphqlgen"
        self.cpp_info.names["cmake_find_package_multi"] = "cppgraphqlgen"

        def _register_components(components):
            for name, requires in components.items():
                self.cpp_info.components[name].names["cmake_find_package"] = name
                self.cpp_info.components[name].names["cmake_find_package_multi"] = name
                self.cpp_info.components[name].libs = [name]
                self.cpp_info.components[name].requires = requires
                if self.settings.os == "Windows" and self.options.shared:
                    self.cpp_info.components[name].defines.append("GRAPHQL_DLLEXPORTS")

        components = {
            "graphqlpeg": ["taocpp-pegtl::taocpp-pegtl"],
            "graphqlresponse": [],
            "graphqlservice": ["graphqlpeg", "graphqlresponse"],
            "graphqlintrospection": ["graphqlservice"],
            "graphqlclient": ["graphqlpeg", "graphqlresponse"],
        }
        if self.options.with_rapidjson:
            components.update({"graphqljson": ["graphqlresponse", "graphqlintrospection", "rapidjson::rapidjson"]})

        _register_components(components)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["graphqlservice"].system_libs.append("pthread")

        if self.options.schemagen or self.options.clientgen:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

            # TODO:
            # - add executables CMake imported targets
            # - boost is not a dependency of cppgraphqlgen libs
            self.cpp_info.components["graphqlservice"].requires.append("boost::program_options")
