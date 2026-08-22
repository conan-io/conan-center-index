from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class SpdlogSetupConan(ConanFile):
    name = "gegles-spdlog_setup"
    description = "Setup spdlog via a TOML config file"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gegles/spdlog_setup"
    topics = ('spdlog', 'logging', 'header-only', 'toml', 'cpptoml')
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "use_std_fmt": [True, False],
    }
    default_options = {
        "use_std_fmt": False,
    }

    @property
    def _min_cppstd(self):
        return 20 if self.options.get_safe("use_std_fmt") else 17

    @property
    def _compilers_minimum_version(self):
        if self.options.get_safe("use_std_fmt"):
            return {
                "Visual Studio": "16",
                "msvc": "192",
                "gcc": "13",
                "clang": "14",
                "apple-clang": "15",
            }
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def config_options(self):
        if Version(self.version) < "1.2.0":
            del self.options.use_std_fmt

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpptoml/0.1.1")
        self.requires("spdlog/[>=1.15 <2]")
        if not self.options.get_safe("use_std_fmt"):
            self.requires("fmt/[*]")

    def configure(self):
        # Match spdlog's use_std_fmt with our own (only if the option exists)
        use_std_fmt = self.options.get_safe("use_std_fmt")
        if use_std_fmt is not None:
            self.options["spdlog"].use_std_fmt = use_std_fmt

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "spdlog_setup")
        self.cpp_info.set_property("cmake_target_name", "spdlog_setup::spdlog_setup")

        if self.options.get_safe("use_std_fmt"):
            self.cpp_info.defines.append("SPDLOG_SETUP_USE_STD_FORMAT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # This is needed since we prefixed the package name with the author name
        self.cpp_info.names["cmake_find_package"] = "SPDLOG_SETUP"
        self.cpp_info.names["cmake_find_package_multi"] = "spdlog_setup"
