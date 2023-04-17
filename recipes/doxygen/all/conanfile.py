from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import pathlib
import yaml

required_conan_version = ">=1.52.0"


class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C++, C, Java, IDL and PHP --- Note: Dot is disabled in this package"
    topics = ("installer", "devtool", "documentation")
    homepage = "https://github.com/doxygen/doxygen"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_parse": [True, False],
        "enable_search": [True, False],
    }
    default_options = {
        "enable_parse": True,
        "enable_search": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _minimum_compiler_version(self):
        if Version(self.version) <= "1.9.1":
            return {
                "gcc": "5",
            }
        return {
            "gcc": "7",  # https://gcc.gnu.org/bugzilla/show_bug.cgi?id=66297
            "Visual Studio": "15",
            "msvc": "191",
        }

    @property
    def _conan_home(self):
        conan_home_env = "CONAN_USER_HOME" if Version(conan_version).major < 2 else "CONAN_HOME"
        conan_home_dir = ".conan" if Version(conan_version).major < 2 else ".conan2"
        return os.environ.get(conan_home_env, pathlib.Path(pathlib.Path.home(), conan_home_dir))

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_search:
            self.requires("xapian-core/1.4.19")
            self.requires("zlib/1.2.13")

    def package_id(self):
        self.info.requires.full_version_mode()

    def compatibility(self):
        # is there a better way of reading all possible versions from settings.yml?
        settings_yml_path = pathlib.Path(self._conan_home, "settings.yml")
        with open(settings_yml_path, "r") as f:
            settings_yml = yaml.safe_load(f)

        compatible_versions = [{"settings": [("compiler.version", v), ("build_type", "Release")]}
            for v in settings_yml["compiler"][str(self.settings.compiler)]["version"] if v <= Version(self.settings.compiler.version)]
        return compatible_versions

    def validate(self):
        minimum_compiler_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if minimum_compiler_version and Version(self.settings.compiler.version) < minimum_compiler_version:
            raise ConanInvalidConfiguration(f"Compiler version too old. At least {minimum_compiler_version} is required.")
        if Version(self.version) == "1.8.18":
            check_min_vs(self, "191")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["build_parse"] = self.options.enable_parse
        tc.variables["build_search"] = self.options.enable_search
        tc.variables["use_libc++"] = self.settings.compiler.get_safe("libcxx") == "libc++"
        tc.variables["win_static"] = is_msvc_static_runtime(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
