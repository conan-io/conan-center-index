from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class UwebsocketsConan(ConanFile):
    name = "uwebsockets"
    description = "Simple, secure & standards compliant web server for the most demanding of applications"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uNetworking/uWebSockets"
    topics = ("websocket", "network", "server", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_zlib": [True, False],
        "with_libdeflate": [True, False],
    }
    default_options = {
        "with_zlib": True,
        "with_libdeflate": False,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7" if Version(self.version) < "20.11.0" else "8",
            "clang": "5" if Version(self.version) < "20.11.0" else "7",
            "apple-clang": "10",
        }

    def config_options(self):
        # libdeflate is not supported before 19.0.0
        if Version(self.version) < "19.0.0":
            del self.options.with_libdeflate

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.get_safe("with_libdeflate"):
            self.requires("libdeflate/1.14")

        if Version(self.version) > "20.17.0":
            self.requires("usockets/0.8.5")
        elif Version(self.version) >= "20.15.0":
            self.requires("usockets/0.8.2")
        elif Version(self.version) >= "19.0.0":
            self.requires("usockets/0.8.1")
        else:
            self.requires("usockets/0.4.0")

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

        if Version(self.version) >= "20.14.0" and self.settings.compiler == "clang" and str(self.settings.compiler.libcxx) == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} needs recent libstdc++ with charconv.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self,
            pattern="*.h",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "include", "uWebSockets"),
            keep_path=False,
        )
        copy(self,
            pattern="*.hpp",
            src=os.path.join(self.source_folder, "src", "f2"),
            dst=os.path.join(self.package_folder, "include", "uWebSockets", "f2"),
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if not self.options.with_zlib:
            self.cpp_info.defines.append("UWS_NO_ZLIB")
        if self.options.get_safe("with_libdeflate"):
            self.cpp_info.defines.append("UWS_USE_LIBDEFLATE")

        self.cpp_info.includedirs.append(os.path.join("include", "uWebSockets"))
