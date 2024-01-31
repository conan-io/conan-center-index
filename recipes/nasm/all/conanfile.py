from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import NMakeToolchain, is_msvc
import os
import shutil

required_conan_version = ">=1.55.0"


class NASMConan(ConanFile):
    name = "nasm"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.nasm.us"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler"
    license = "BSD-2-Clause"
    topics = ("asm", "installer", "assembler",)

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _nasm(self):
        suffix = "w.exe" if is_msvc(self) else ""
        return os.path.join(self.package_folder, "bin", f"nasm{suffix}")

    @property
    def _ndisasm(self):
        suffix = "w.exe" if is_msvc(self) else ""
        return os.path.join(self.package_folder, "bin", f"ndisasm{suffix}")

    def _chmod_plus_x(self, filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
            if not is_msvc(self):
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            if self.settings.arch == "x86":
                tc.extra_cflags.append("-m32")
            elif self.settings.arch == "x86_64":
                tc.extra_cflags.append("-m64")
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run(f'nmake /f {os.path.join("Mkfiles", "msvc.mak")}')
        else:
            with chdir(self, self.source_folder):
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
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
        self._chmod_plus_x(self._nasm)
        self._chmod_plus_x(self._ndisasm)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        compiler_executables = {"asm": self._nasm}
        self.conf_info.update("tools.build:compiler_executables", compiler_executables)
        self.buildenv_info.define_path("NASM", self._nasm)
        self.buildenv_info.define_path("NDISASM", self._ndisasm)
        self.buildenv_info.define_path("AS", self._nasm)

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.NASM = self._nasm
        self.env_info.NDISASM = self._ndisasm
        self.env_info.AS = self._nasm
