from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get, chdir, replace_in_file, copy, rmdir
from conan.tools.microsoft import is_msvc
from conans import tools, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment
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
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
        return self._env_build

    #def validate(self):
    #    if Version(self.version) < "2.1.0-beta1" and self.settings.os == "Macos" and self.settings.arch == "armv8":
    #        raise ConanInvalidConfiguration(f"{self.ref} is not supported by Mac M1. Please, try any version >=2.1")

    def build(self):
        if is_msvc(self):
            with chdir(self, os.path.join(self._source_subfolder, 'src')):
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars), tools.vcvars(self):
                    variant = '' if self.options.shared else 'static'
                    self.run("msvcbuild.bat %s" % variant)
        else:
            buildmode = 'shared' if self.options.shared else 'static'
            makefile = os.path.join(self._source_subfolder, 'src', 'Makefile')
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
            env = dict()
            if self.settings.os == "Macos":
                # Per https://luajit.org/install.html: If MACOSX_DEPLOYMENT_TARGET
                # is not set then it's forced to 10.4, which breaks compile on Mojave.
                version = self.settings.get_safe("os.version")
                if not version and platform.system() == "Darwin":
                    macversion = Version(platform.mac_ver()[0])
                    version = f"{macversion.major}.{macversion.minor}"
                env["MACOSX_DEPLOYMENT_TARGET"] = version
            with chdir(self, self._source_subfolder), tools.environment_append(env):
                env_build = self._configure_autotools()
                compiler = "clang" if "clang" in str(self.settings.compiler) else str(self.settings.compiler)
                compiler = tools.get_env("CC", compiler)
                env_build.make(args=[f"PREFIX={self.package_folder}", f"CC={compiler}"])

    def package(self):
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, self._source_subfolder))
        if is_msvc(self):
            ljs = os.path.join(self.build_folder, self._source_subfolder, "src")
            inc = os.path.join(self.package_folder, "include", "luajit-2.0")
            self.copy("lua.h", dst=inc, src=ljs)
            self.copy("lualib.h", dst=inc, src=ljs)
            self.copy("lauxlib.h", dst=inc, src=ljs)
            self.copy("luaconf.h", dst=inc, src=ljs)
            self.copy("lua.hpp", dst=inc, src=ljs)
            self.copy("luajit.h", dst=inc, src=ljs)
            self.copy("lua51.lib", dst="lib", src=ljs)
            self.copy("lua51.dll", dst="bin", src=ljs)
        else:
            with chdir(self, self._source_subfolder):
                env_build = self._configure_autotools()
                env_build.install(args=["PREFIX=%s" % self.package_folder])
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["lua51" if is_msvc(self) else "luajit-5.1"]
        luaversion = Version(self.version)
        self.cpp_info.includedirs = [os.path.join("include", f"luajit-{luaversion.major}.{luaversion.minor}")]
        self.output.info(f"***** INCLUDE DIRS: {self.cpp_info.includedirs}")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "dl"])
