import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy

required_conan_version = ">=2"


class CtreConan(ConanFile):
    name = "ctre"
    description = "Compile Time Regular Expression for C++17/20"
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hanickadot/compile-time-regular-expressions"
    topics = ("cpp17", "regex", "compile-time-regular-expressions", "header-only")
    package_type = "header-library"
    settings = "compiler"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        compiler = self.settings.compiler
        compiler_version = Version(self.settings.compiler.version)

        check_min_cppstd(self, "17")
        if is_msvc(self):
            if compiler_version < 16:
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support MSVC < 16")
        elif compiler == "gcc" and compiler_version < 8:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 8")
        elif compiler == "clang":
            if compiler_version < "6.0":
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support clang < 6.0")
        elif compiler == "apple-clang":
            if compiler_version < "10.0":
                raise ConanInvalidConfiguration(f"{self.ref} doesn't support Apple clang < 10.0")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],  strip_root=True)

    def package(self):
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
