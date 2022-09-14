from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get, chdir, replace_in_file, copy, rmdir
from conan.tools.microsoft import is_msvc, MSBuildToolchain, VCVars
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import Environment
from conan.errors import ConanInvalidConfiguration
import os
import platform


required_conan_version = ">=1.50.0"


class LuajitConan(ConanFile):
    name = "luajit"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://luajit.org"
    description = "LuaJIT is a Just-In-Time Compiler (JIT) for the Lua programming language."
    topics = ("lua", "jit")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
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

    def validate(self):
        if Version(self.version) < "2.1.0-beta1" and self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported by Mac M1. Please, try any version >=2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            tc = VCVars(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            if self.info.settings.os == "Macos":
                env = Environment()
                env.define("MACOSX_DEPLOYMENT_TARGET", self._macosx_deployment_target)
                env.define("SYSTEM_VERSION_COMPAT", 1)
                envvars = env.vars(self, scope="build")
                envvars.save_script("conanbuildenv_macosx_deploy_target")

    def _patch_sources(self):
        if not is_msvc(self):
            buildmode = 'shared' if self.options.shared else 'static'
            makefile = os.path.join(self.source_folder, 'src', 'Makefile')
            replace_in_file(self, makefile,
                                  'BUILDMODE= mixed',
                                  'BUILDMODE= %s' % buildmode)
            replace_in_file(self, makefile,
                                  'TARGET_DYLIBPATH= $(TARGET_LIBPATH)/$(TARGET_DYLIBNAME)',
                                  'TARGET_DYLIBPATH= $(TARGET_DYLIBNAME)')
            # adjust mixed mode defaults to build either .so or .a, but not both
            if not self.options.shared:
                replace_in_file(self, makefile,
                                      'TARGET_T= $(LUAJIT_T) $(LUAJIT_SO)',
                                      'TARGET_T= $(LUAJIT_T) $(LUAJIT_A)')
                replace_in_file(self, makefile,
                                      'TARGET_DEP= $(LIB_VMDEF) $(LUAJIT_SO)',
                                      'TARGET_DEP= $(LIB_VMDEF) $(LUAJIT_A)')
            else:
                replace_in_file(self, makefile,
                                      'TARGET_O= $(LUAJIT_A)',
                                      'TARGET_O= $(LUAJIT_SO)')
            if "clang" in str(self.settings.compiler):
                replace_in_file(self, makefile, 'CC= $(DEFAULT_CC)', 'CC= clang')

    @property
    def _macosx_deployment_target(self):
        # Per https://luajit.org/install.html: If MACOSX_DEPLOYMENT_TARGET
        # is not set then it's forced to 10.4, which breaks compile on Mojave.
        version = self.settings.get_safe("os.version")
        if not version and platform.system() == "Darwin":
            macversion = Version(platform.mac_ver()[0])
            version = f"{macversion.major}.{macversion.minor}"
        return version

    def build(self):
        if is_msvc(self):
            variant = '' if self.options.shared else 'static'
            self.run("msvcbuild.bat %s" % variant, env="conanrun")
        else:
            self._patch_sources()
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.make(args=[f"PREFIX={self.package_folder}"])

    def package(self):
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        src_folder = os.path.join(self.source_folder, "src")
        include_folder = os.path.join(self.package_folder, "include")
        if is_msvc(self):
            copy(self, "lua.h", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "lualib.h", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "lauxlib.h", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "luaconf.h", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "lua.hpp", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "luajit.h", src=src_folder, dst=os.path.join(include_folder, "luajit-2.0"))
            copy(self, "lua51.lib", src=src_folder, dst=os.path.join(self.package_folder, "lib"))
            copy(self, "lua51.dll", src=src_folder, dst=os.path.join(self.package_folder, "bin"))
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install(args=[f"PREFIX={self.package_folder}"])
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["lua51" if is_msvc(self) else "luajit-5.1"]
        luaversion = Version(self.version)
        self.cpp_info.includedirs = [os.path.join("include", f"luajit-{luaversion.major}.{luaversion.minor}")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "dl"])
