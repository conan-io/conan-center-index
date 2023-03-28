import os

from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.51.0"

class CMakeConan(ConanFile):
    package_type = "application"
    description = "CMake, the cross-platform, open-source build system."
    topics = ("build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False],
        "from_sources": [True, False],
    }
    default_options = {
        "with_openssl": True,
        "from_sources": False,
    }

    def set_name(self):
        self.name = os.environ.get('CMAKE_RECIPE_NAME', 'cmake')
        print(self.name)

    def config_options(self):
        if self.settings.os not in ["Macos", "Windows", "Linux"]:
            self.options.from_sources = True
        if self.settings.os == "Windows" and self.options.from_sources:
            self.options.with_openssl = False

    def validate(self):
        if self.settings.arch not in ["x86_64", "armv8"]:
            raise ConanInvalidConfiguration("CMake binaries are only provided for x86_64 and armv8 architectures")

        if self.settings.os == "Windows" and self.settings.arch == "armv8" and Version(self.version) < "3.24":
            raise ConanInvalidConfiguration("CMake only supports ARM64 binaries on Windows starting from 3.24")

    def build(self):
        arch = str(self.settings.arch) if self.settings.os != "Macos" else "universal"
        get(self, **self.conan_data["binaries"][self.version][str(self.settings.os)][arch],
            destination=self.source_folder, strip_root=True)

    def package_id(self):
        if self.info.settings.os == "Macos":
            del self.info.settings.arch
        del self.info.settings.compiler
        # The compatibility() method is not compatible with package_id() deleting values from info,
        # so make the packages compatible despite sources or openssl, by deleting those settings.
        # See: https://github.com/conan-io/conan/issues/12476
        del self.info.options.from_sources
        del self.info.options.with_openssl

    def package(self):
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

        if self.settings.os == "Macos":
            docs_folder = os.path.join(self.build_folder, "CMake.app", "Contents", "doc", "cmake")
        else:
            docs_folder = os.path.join(self.build_folder, "doc", "cmake")

        copy(self, "Copyright.txt", src=docs_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

        if self.settings.os != "Macos":
            # Remove unneeded folders (also cause long paths on Windows)
            # Note: on macOS we don't want to modify the bundle contents
            #       to preserve signature validation
            rmdir(self, os.path.join(self.package_folder, "doc"))
            rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Macos" and not self.options.from_sources:
            bindir = os.path.join(self.package_folder, "CMake.app", "Contents", "bin")
            self.cpp_info.bindirs = [bindir]
        else:
            bindir = os.path.join(self.package_folder, "bin")

        # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
