import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save, rename
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.54.0"


class LibdatrieConan(ConanFile):
    name = "libdatrie"
    description = "Implementation of double-array structure for representing tries"
    license = "LGPL-2.1-or-later"
    homepage = "https://linux.thai.net/projects/datrie"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("trie", "double-array-trie", "datrie")

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
        "tools": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("libiconv/1.17")

    def validate(self):
        if is_apple_os(self) and self.options.shared:
            # Fails due to build script bugs
            raise ConanInvalidConfiguration("shared builds on Apple OS-s are not supported. Contributions are welcome!")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-doxygen-doc",
        ])
        if is_msvc(self):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            iconv_info = self.dependencies["libiconv"].cpp_info
            env.append("CPPFLAGS", [f"-I{unix_path(self, iconv_info.includedir)}"] + [f"-D{d}" for d in iconv_info.defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in iconv_info.libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, iconv_info.libdir)}"])
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            tc = AutotoolsDeps(self)
            tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        if not self.options.tools:
            save(self, os.path.join(self.build_folder, "tools", "Makefile"), "all:\n\t\ninstall:\n\t\n")
        # Unnecessary and breaks MSVC build
        save(self, os.path.join(self.build_folder, "man", "Makefile"), "all:\n\t\ninstall:\n\t\n")
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "datrie.dll.lib"),
                   os.path.join(self.package_folder, "lib", "datrie.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "datrie-0.2")
        self.cpp_info.libs = ["datrie"]
