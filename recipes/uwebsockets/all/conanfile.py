import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class UwebsocketsConan(ConanFile):
    name = "uwebsockets"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Simple, secure & standards compliant web server for the most demanding of applications"
    license = "Apache-2.0"
    homepage = "https://github.com/uNetworking/uWebSockets"
    topics = ("websocket", "network", "server", )
    settings = "compiler"
    no_copy_source = True
    options = {
        "with_zlib": [True, False,],
        "with_libdeflate": [True, False,],
    }
    default_options = {
        "with_zlib": True,
        "with_libdeflate": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        # libdeflate is not supported before 19.0.0
        if tools.Version(self.version) < "19.0.0":
            del self.options.with_libdeflate

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

        minimal_version = {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support"
                % (self.name, compiler)
            )
            self.output.warn(
                "%s requires a compiler that supports at least C++%s"
                % (self.name, minimal_cpp_standard)
            )
            return

        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports at least C++%s"
                % (self.name, minimal_cpp_standard)
            )

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_libdeflate", False):
            self.requires("libdeflate/1.8")

        if tools.Version(self.version) >= "19.0.0":
            self.requires("usockets/0.8.1")
        else:
            self.requires("usockets/0.4.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            pattern="*.h",
            src=os.path.join(self._source_subfolder, "src"),
            dst=os.path.join("include", "uWebSockets"),
            keep_path=False,
        )
        self.copy(
            pattern="*.hpp",
            src=os.path.join(self._source_subfolder, "src", "f2"),
            dst=os.path.join("include", "uWebSockets", "f2"),
            keep_path=False,
        )

    def package_id(self):
        self.settings.clear()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "uWebSockets"))
        if not self.options.with_zlib:
            self.cpp_info.defines.append("UWS_NO_ZLIB")
        if self.options.get_safe("with_libdeflate", False):
            self.cpp_info.defines.append("UWS_USE_LIBDEFLATE")
        self.cpp_info.filenames["cmake_find_package"] = "uwebsockets"
        self.cpp_info.filenames["cmake_find_package_multi"] = "uwebsockets"
