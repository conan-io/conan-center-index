from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class Jinja2cppConan(ConanFile):
    name = "jinja2cpp"
    license = "MIT"
    homepage = "https://jinja2cpp.dev/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Jinja2 C++ (and for C++) almost full-conformance template engine implementation"
    topics = ("conan", "cpp14", "cpp17", "jinja2", "string templates", "templates engine")
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

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
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)

    def requirements(self):
        self.requires("boost/1.76.0")
        self.requires("expected-lite/0.5.0")
        self.requires("optional-lite/3.4.0")
        self.requires("rapidjson/cci.20200410")
        self.requires("string-view-lite/1.6.0")
        self.requires("variant-lite/2.0.0")
        if self.version == "1.1.0":
            self.requires("fmt/6.2.1") # not compatible with fmt >= 7.0.0
        else:
            self.requires("nlohmann_json/3.10.2")
            self.requires("fmt/8.0.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Don't force MD for shared lib, allow to honor runtime from profile
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(JINJA2CPP_MSVC_RUNTIME_TYPE \"/MD\")", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JINJA2CPP_BUILD_TESTS"] = False
        self._cmake.definitions["JINJA2CPP_STRICT_WARNINGS"] = False
        self._cmake.definitions["JINJA2CPP_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["JINJA2CPP_DEPS_MODE"] = "conan-build"
        self._cmake.definitions["JINJA2CPP_CXX_STANDARD"] = self.settings.compiler.get_safe("cppstd", 14)
        # Conan cmake generator omits the build_type flag for MSVC multiconfiguration CMake,
        # but provide build-type-specific runtime type flag. For now, Jinja2C++ build scripts
        # need to know the build type is being built in order to setup internal flags correctly
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        compiler = self.settings.get_safe("compiler")
        if compiler == "Visual Studio":
            # Runtime type configuration for Jinja2C++ should be strictly '/MT' or '/MD'
            runtime = self.settings.get_safe("compiler.runtime")
            if runtime == "MTd":
                runtime = "MT"
            if runtime == "MDd":
                runtime = "MD"
            self._cmake.definitions["JINJA2CPP_MSVC_RUNTIME_TYPE"] = "/" + runtime
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.version == "1.1.0":
            if tools.Version(self.deps_cpp_info["fmt"].version) >= "7.0.0":
                raise ConanInvalidConfiguration("jinja2cpp requires fmt < 7.0.0")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "jinja2cpp"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_subfolder, self._module_file),
            {"jinja2cpp": "jinja2cpp::jinja2cpp"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "jinja2cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "jinja2cpp"
        self.cpp_info.builddirs.append(self._module_subfolder)
        module_rel_path = os.path.join(self._module_subfolder, self._module_file)
        self.cpp_info.build_modules["cmake_find_package"] = [module_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [module_rel_path]
        self.cpp_info.libs = ["jinja2cpp"]
