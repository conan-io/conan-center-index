import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class ConanXqilla(ConanFile):
    name = "xsd"
    description = (
        "XSD is a W3C XML Schema to C++ translator. "
        "It generates vocabulary-specific, statically-typed C++ mappings (also called bindings) from XML Schema definitions. "
        "XSD supports two C++ mappings: in-memory C++/Tree and event-driven C++/Parser."
    )
    license = ("GPL-2.0", "FLOSSE")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codesynthesis.com/projects/xsd/"
    topics = ("xml", "c++")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/3.2.3")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("The xsd recipe currently only supports Linux.")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.extra_cxxflags = ["-std=c++11"]
        tc.extra_ldflags = ["-pthread"]
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "xsd"))
        copy(self, "GPLv2",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "xsd"))
        copy(self, "FLOSSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "xsd"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=[f"install_prefix={self.package_folder}"])
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.path.append(bin_path)
