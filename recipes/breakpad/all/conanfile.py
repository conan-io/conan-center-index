from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class BreakpadConan(ConanFile):
    name = "breakpad"
    description = "A set of client and server components which implement a crash-reporting system"
    topics = ["crash", "report", "breakpad"]
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://chromium.googlesource.com/breakpad/breakpad/"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("linux-syscall-support/cci.20200813", transitive_headers=True)

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Breakpad can only be built on Linux. For other OSs check sentry-breakpad")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        # see https://github.com/conan-io/conan/issues/12020
        tc.configure_args.append("--libexecdir=${prefix}/bin")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["libbreakpad"].set_property("pkg_config_name", "breakpad")
        self.cpp_info.components["libbreakpad"].libs = ["breakpad"]
        self.cpp_info.components["libbreakpad"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["libbreakpad"].system_libs.append("pthread")
        self.cpp_info.components["libbreakpad"].requires.append("linux-syscall-support::linux-syscall-support")

        self.cpp_info.components["client"].set_property("pkg_config_name", "breakpad-client")
        self.cpp_info.components["client"].libs = ["breakpad_client"]
        self.cpp_info.components["client"].includedirs.append(os.path.join("include", "breakpad"))
        self.cpp_info.components["client"].system_libs.append("pthread")
        self.cpp_info.components["client"].requires.append("linux-syscall-support::linux-syscall-support")

        # workaround to always produce a global pkgconfig file for PkgConfigDeps
        self.cpp_info.set_property("pkg_config_name", "breakpad-do-not-use")

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
