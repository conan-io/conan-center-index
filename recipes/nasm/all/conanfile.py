import os
import shutil

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rmdir, apply_conandata_patches, export_conandata_patches, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc

required_conan_version = ">=1.52.0"


class NASMConan(ConanFile):
    name = "nasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.nasm.us"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler"
    license = "BSD-2-Clause"
    topics = ("nasm", "installer", "assembler")

    settings = "os", "arch", "compiler", "build_type"


    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.info.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package_id(self):
        del self.info.settings.compiler

    def generate(self):
        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            VCVars(self).generate()
            tc.configure_args.append("-nologo")
        if self.settings.arch == "x86":
            tc.extra_cflags.append("-m32")
        elif self.settings.arch == "x86_64":
            tc.extra_cflags.append("-m64")
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()


    def build(self):
        apply_conandata_patches(self)

        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run("nmake /f {}".format(os.path.join("Mkfiles", "msvc.mak")))
        else:
            autotools = Autotools(self)
            autotools.configure()

            # GCC9 - "pure" attribute on function returning "void"
            replace_in_file(self, "Makefile", "-Werror=attributes", "")

            # Need "-arch" flag for the linker when cross-compiling.
            # FIXME: Revisit after https://github.com/conan-io/conan/issues/9069, using new Autotools integration
            # TODO it is time to revisit, not sure what to do here though...
            if str(self.version).startswith("2.13"):
                replace_in_file(self, "Makefile", "$(CC) $(LDFLAGS) -o", "$(CC) $(ALL_CFLAGS) $(LDFLAGS) -o")
                replace_in_file(self, "Makefile", "$(INSTALLROOT)", "$(DESTDIR)")
            autotools.make()


    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, pattern="*.exe", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            with chdir(self, os.path.join(self.package_folder, "bin")):
                shutil.copy2("nasm.exe", "nasmw.exe")
                shutil.copy2("ndisasm.exe", "ndisasmw.exe")
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
