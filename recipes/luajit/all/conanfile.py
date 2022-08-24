import os
import platform
from conan import ConanFile, tools
from conans import VisualStudioBuildEnvironment, AutoToolsBuildEnvironment


class LuajitConan(ConanFile):
    name = "luajit"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://luajit.org"
    description = "LuaJIT is a Just-In-Time Compiler (JIT) for the Lua programming language."
    topics = ("conan", "lua", "jit")
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
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.files.chdir(self, os.path.join(self._source_subfolder, 'src')):
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars), tools.vcvars(self):
                    variant = '' if self.options.shared else 'static'
                    self.run("msvcbuild.bat %s" % variant)
        else:
            buildmode = 'shared' if self.options.shared else 'static'
            makefile = os.path.join(self._source_subfolder, 'src', 'Makefile')
            tools.files.replace_in_file(self, makefile,
                                  'BUILDMODE= mixed',
                                  'BUILDMODE= %s' % buildmode)
            tools.files.replace_in_file(self, makefile,
                                  'TARGET_DYLIBPATH= $(TARGET_LIBPATH)/$(TARGET_DYLIBNAME)',
                                  'TARGET_DYLIBPATH= $(TARGET_DYLIBNAME)')
            # adjust mixed mode defaults to build either .so or .a, but not both
            if not self.options.shared:
                tools.files.replace_in_file(self, makefile,
                                      'TARGET_T= $(LUAJIT_T) $(LUAJIT_SO)',
                                      'TARGET_T= $(LUAJIT_T) $(LUAJIT_A)')
                tools.files.replace_in_file(self, makefile,
                                      'TARGET_DEP= $(LIB_VMDEF) $(LUAJIT_SO)',
                                      'TARGET_DEP= $(LIB_VMDEF) $(LUAJIT_A)')
            else:
                tools.files.replace_in_file(self, makefile,
                                      'TARGET_O= $(LUAJIT_A)',
                                      'TARGET_O= $(LUAJIT_SO)')
            env = dict()
            if self.settings.os == "Macos":
                # Per https://luajit.org/install.html: If MACOSX_DEPLOYMENT_TARGET
                # is not set then it's forced to 10.4, which breaks compile on Mojave.
                version = self.settings.get_safe("os.version")
                if not version and platform.system() == "Darwin":
                    major, minor, _ = platform.mac_ver()[0].split(".")
                    version = "%s.%s" % (major, minor)
                env["MACOSX_DEPLOYMENT_TARGET"] = version
            with tools.files.chdir(self, self._source_subfolder), tools.environment_append(env):
                env_build = self._configure_autotools()
                env_build.make(args=["PREFIX=%s" % self.package_folder])

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == 'Visual Studio':
            ljs = os.path.join(self._source_subfolder, "src")
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
            with tools.files.chdir(self, self._source_subfolder):
                env_build = self._configure_autotools()
                env_build.install(args=["PREFIX=%s" % self.package_folder])
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["lua51" if self.settings.compiler == "Visual Studio" else "luajit-5.1"]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include", "luajit-2.0")]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "dl"])
