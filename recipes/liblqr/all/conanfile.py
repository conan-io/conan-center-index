from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.54.0"


class LibLqrConan(ConanFile):
    name = "liblqr"
    description = (
        "The LiquidRescale (lqr) library provides a C/C++ API for performing "
        "non-uniform resizing of images by the seam-carving technique."
    )
    license = ("LGPL-3.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://liblqr.wikidot.com"
    topics = ("image", "resizing", "seam-carving")
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
    def _is_cl_like(self):
        return self.settings.compiler.get_safe("runtime") is not None

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        if self._is_cl_like:
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.81.0", transitive_headers=True)

    def build_requirements(self):
        if not self._is_cl_like:
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/[>=2.2 <3]")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self._is_cl_like:
            tc = CMakeToolchain(self)
            tc.variables["LQR_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.append("--disable-install-man")
            if self.settings.os == "Windows":
                # This option in upstream configure.ac must be disabled for static
                # windows build, to avoid adding __declspec(dllexport) in front
                # of declarations during build.
                tc.configure_args.append(f"--enable-declspec={yes_no(self.options.shared)}")
            tc.generate()

            deps = PkgConfigDeps(self)
            deps.generate()

    def build(self):
        if self._is_cl_like:
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self._is_cl_like:
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "lqr-1")
        self.cpp_info.includedirs = [os.path.join("include", "lqr-1")]
        self.cpp_info.libs = ["lqr-1"]
        self.cpp_info.requires = ["glib::glib-2.0"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("LQR_DISABLE_DECLSPEC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
