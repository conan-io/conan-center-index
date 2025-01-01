import os
import shutil
from pathlib import Path

from conan import ConanFile
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.4"


class GStOrcConan(ConanFile):
    name = "gst-orc"
    description = "Optimized Inner Loops Runtime Compiler for very simple programs that operate on arrays of data."
    license = "BSD-2-Clause AND BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/gstreamer/orc"
    topics = ("compiler", "simd", "vectorization")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
    }
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["orc-backend"] = "all"
        tc.project_options["tools"] = "enabled" if self.options.tools else "disabled"
        tc.project_options["benchmarks"] = "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["gtk_doc"] = "disabled"
        tc.project_options["orc-test"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.project_options["default_library"] = "shared" if self.options.shared else "static"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        if is_msvc(self):
            for filename_old in Path(path).glob("*.a"):
                filename_new = str(filename_old)[:-2] + ".lib"
                shutil.move(filename_old, filename_new)

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        version = Version(self.version)
        pkg_name = f"orc-{version.major}.{version.minor}"
        component = self.cpp_info.components[pkg_name]
        component.set_property("pkg_config_name", pkg_name)
        component.libs = [pkg_name]
        component.includedirs = [os.path.join("include", pkg_name)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            component.system_libs = ["m", "pthread"]
        elif self.settings.os == "Android":
            component.system_libs = ["log"]
        if self.options.tools:
            component.set_property("pkg_config_custom_content",
                                       "toolsdir=${prefix}/bin\n"
                                       "orcc=${toolsdir}/orcc\n")
