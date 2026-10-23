from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import stdcpp_library
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.10.0"


class LibVmafConan(ConanFile):
    name = "libvmaf"
    description = (
        "Perceptual video quality assessment based on multi-method fusion (VMAF)."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Netflix/vmaf"
    license = "BSD-2-Clause-Patent"
    topics = ("video", "quality", "metrics", "vmaf", "netflix")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _repo_folder(self):
        # Repository root, one level above the Meson project folder.
        return os.path.dirname(self.source_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")
        # The Meson project is in the "libvmaf" subfolder of the repository.
        self.folders.source = os.path.join("src", "libvmaf")

    def build_requirements(self):
        self.tool_requires("meson/[>=1 <2]")
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/[>=2.13.02 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
            destination=self._repo_folder)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["enable_tests"] = False
        tc.project_options["enable_docs"] = False
        tc.project_options["enable_tools"] = False
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE",
             src=self._repo_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libvmaf")
        self.cpp_info.libs = ["vmaf"]
        # Consumers such as FFmpeg include <libvmaf.h> directly
        self.cpp_info.includedirs = ["include", os.path.join("include", "libvmaf")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
