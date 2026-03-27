import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, rm, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps

required_conan_version = ">=2.0"


class TwoLAMEConan(ConanFile):
    name = "twolame"
    version = "0.4.0"
    description = "TwoLAME is an optimised MPEG Audio Layer 2 (MP2) encoder"
    license = "LGPL-2.1-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.twolame.org"
    topics = ("mp2", "mpeg", "audio", "encoder", "twolame")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    languages = "C"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cli": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_cli": False,
    }
    options_description = {
        "shared": "Build as shared library (DLL/.so/.dylib) instead of static (.lib/.a)",
        "fPIC": "Generate position-independent code, required for shared libraries on Linux/macOS",
        "with_cli": "Build the command-line encoder (requires libsndfile; disabled on Windows due to missing POSIX headers)",
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # CLI requires POSIX headers (unistd.h, getopt.h)
            del self.options.with_cli

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.get_safe("with_cli"):
            self.requires("libsndfile/[>=1.2]")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("pkgconf/[>=2.1]")
            self.tool_requires("autoconf/2.71")
            self.tool_requires("automake/1.16.5")
            self.tool_requires("libtool/2.4.7")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.variables["TWOLAME_SRC_DIR"] = self.source_folder.replace("\\", "/")
            tc.generate()
            deps = CMakeDeps(self)
            deps.generate()
        else:
            deps = AutotoolsDeps(self)
            deps.generate()
            pkgconfig = PkgConfigDeps(self)
            pkgconfig.generate()
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-static={yes_no(not self.options.shared)}",
                "--with-sndfile" if self.options.with_cli else "--without-sndfile",
            ])
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "twolame")
        self.cpp_info.libs = ["twolame"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBTWOLAME_STATIC")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("m")
