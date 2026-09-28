from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.files import copy, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Git
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
        "with_asm": [True, False],
        "with_tools": [True, False],
        "built_in_models": [True, False],
        "enable_float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_asm": True,
        "built_in_models": True,
        "enable_float": False,
        "with_tools": False,
    }

    options_description = {
        "with_asm": "Enable assembly optimizations, if available",
        "with_tools": "Build command-line tools",
        "built_in_models": "Include built-in VMAF models",
        "enable_float": "Enable floating point calculations",
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
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.options.with_asm and self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/[>=2.13.02 <3]")

    def source(self):
        # The Meson project lives in the "libvmaf" subfolder, but the default
        # models compiled into the library are stored in the repository's
        # top-level "model" folder, so the whole repository is cloned.
        git = Git(self, folder=self._repo_folder)
        git.fetch_commit(**self.conan_data["sources"][self.version])

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options["enable_tests"] = False
        tc.project_options["enable_docs"] = False
        tc.project_options["enable_tools"] = self.options.with_tools
        tc.project_options["enable_asm"] = self.options.with_asm
        tc.project_options["built_in_models"] = self.options.built_in_models
        tc.project_options["enable_float"] = self.options.enable_float
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
        fix_apple_shared_install_name(self)
        if is_msvc(self) and not self.options.shared:
            os.rename(os.path.join(self.package_folder, "lib", "libvmaf.a"),
                      os.path.join(self.package_folder, "lib", "vmaf.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libvmaf")
        self.cpp_info.libs = ["vmaf"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
