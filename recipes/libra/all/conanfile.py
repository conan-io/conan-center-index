import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout

required_conan_version = ">=2.1"


class LibraConan(ConanFile):
    name = "libra"
    description = "Declarative CMake framework for C/C++ project configuration, analysis, formatting, testing and packaging"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jharwell/libra"
    topics = ("cmake", "build-system", "cmake-modules", "clang-tidy", "clang-format")
    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        # Settings exist only so validate() can inspect the platform; the
        # packaged CMake modules are identical everywhere.
        self.info.clear()

    def validate(self):
        # Platform support only; compiler minimums are enforced by LIBRA's CMake.
        if self.settings.os == "Windows" or self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration(f"{self.ref} does not support Windows/MSVC.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

        # CMake modules, minus LIBRA's own packaging helpers: Conan handles
        # packaging for consumers.
        copy(
            self,
            "*.cmake",
            src=os.path.join(self.source_folder, "cmake", "libra"),
            dst=os.path.join(self.package_folder, "cmake", "libra"),
            excludes=["package/*"],
        )

        # Default tool configs (.clang-format, .clang-tidy, .cmake-format).
        for pattern in ("*.clang-format", "*.clang-tidy", "*.cmake-format"):
            copy(
                self,
                pattern,
                src=os.path.join(self.source_folder, "dots"),
                dst=os.path.join(self.package_folder, "dots"),
            )

        # The package has no .git, so version.cmake falls back to self.cmake.
        # Pin it to the packaged version rather than trusting the tarball copy.
        save(
            self,
            os.path.join(self.package_folder, "cmake", "libra", "self.cmake"),
            f'set(LIBRA_VERSION "{self.version}")\n',
        )

    def package_info(self):
        # Consumers write include(libra/<module>).
        self.cpp_info.builddirs = ["cmake"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
