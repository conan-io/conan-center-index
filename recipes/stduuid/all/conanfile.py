from conan import ConanFile, tools$
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=1.33.0"

class StduuidConan(ConanFile):
    name = "stduuid"
    description = "A C++17 cross-platform implementation for UUIDs"
    topics = ("uuid", "guid")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mariusbancila/stduuid"
    settings = "os", "compiler"
    options = {
        "with_cxx20_span": [True, False],
    }
    default_options = {
        "with_cxx20_span": False,
    }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if not self.options.with_cxx20_span:
            self.requires("ms-gsl/2.0.0")
        if self.settings.os == "Linux" and tools.scm.Version(self.version) <= "1.0":
            self.requires("libuuid/1.0.3")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def validate(self):
        version = Version(self.settings.compiler.version)
        compiler = self.settings.compiler
        if self.settings.compiler.cppstd and \
           not any([str(self.settings.compiler.cppstd) == std for std in ["17", "20", "gnu17", "gnu20"]]):
            raise ConanInvalidConfiguration("stduuid requires at least c++17")
        elif compiler == "Visual Studio"and version < "15":
            raise ConanInvalidConfiguration("stduuid requires at least Visual Studio version 15")
        else:
            if ( compiler == "gcc" and version < "7" ) or ( compiler == "clang" and version < "5" ):
                raise ConanInvalidConfiguration("stduuid requires a compiler that supports at least C++17")
            elif compiler == "apple-clang"and version < "10":
                raise ConanInvalidConfiguration("stduuid requires a compiler that supports at least C++17")

    def package(self):
        root_dir = self._source_subfolder
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=root_dir)
        self.copy(pattern="uuid.h", dst="include", src=include_dir)

    def package_info(self):
        if not self.options.with_cxx20_span:
            self.cpp_info.includedirs.append(os.path.join(self.deps_cpp_info["ms-gsl"].include_paths[0], "gsl"))

