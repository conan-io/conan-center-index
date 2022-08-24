from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class Jinja2cppConan(ConanFile):
    name = "jinja2cpp"
    license = "MIT"
    homepage = "https://jinja2cpp.dev/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Jinja2 C++ (and for C++) almost full-conformance template engine implementation"
    topics = ("cpp14", "cpp17", "jinja2", "string templates", "templates engine")

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
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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
        self.requires("boost/1.78.0")
        self.requires("expected-lite/0.5.0")
        self.requires("optional-lite/3.5.0")
        self.requires("rapidjson/cci.20211112")
        self.requires("string-view-lite/1.6.0")
        self.requires("variant-lite/2.0.0")
        if self.version == "1.1.0":
            self.requires("fmt/6.2.1") # not compatible with fmt >= 7.0.0
        else:
            self.requires("nlohmann_json/3.10.5")
            self.requires("fmt/8.1.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 14)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Don't force MD for shared lib, allow to honor runtime from profile
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
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
        if self._is_msvc:
            # Runtime type configuration for Jinja2C++ should be strictly '/MT' or '/MD'
            runtime = "/MD" if "MD" in msvc_runtime_flag(self) else "/MT"
            self._cmake.definitions["JINJA2CPP_MSVC_RUNTIME_TYPE"] = runtime
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
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "jinja2cpp"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
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
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jinja2cpp")
        self.cpp_info.set_property("cmake_target_name", "jinja2cpp")
        self.cpp_info.libs = ["jinja2cpp"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
