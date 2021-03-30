import os
from conans import ConanFile, tools, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment


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
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.chdir(os.path.join(self._source_subfolder, 'src')):
                env_build = VisualStudioBuildEnvironment(self)
                with tools.environment_append(env_build.vars), tools.vcvars(self):
                    variant = '' if self.options.shared else 'static'
                    self.run("msvcbuild.bat %s" % variant)
        else:
            buildmode = 'shared' if self.options.shared else 'static'
            tools.replace_in_file(os.path.join(self._source_subfolder, 'src', 'Makefile'),
                                  'BUILDMODE= mixed',
                                  'BUILDMODE= %s' % buildmode)
            with tools.chdir(self._source_subfolder):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        ljs = os.path.join(self._source_subfolder, "src")
        self.copy("lua.h", dst="include", src=ljs)
        self.copy("lualib.h", dst="include", src=ljs)
        self.copy("lauxlib.h", dst="include", src=ljs)
        self.copy("luaconf.h", dst="include", src=ljs)
        self.copy("lua.hpp", dst="include", src=ljs)
        self.copy("luajit.h", dst="include", src=ljs)
        self.copy("lua51.lib", dst="lib", src=ljs)
        self.copy("lua51.dll", dst="bin", src=ljs)
        self.copy("libluajit.a", dst="lib", src=ljs)
        self.copy("libluajit*.so", dst="lib", src=ljs)
        self.copy("libluajit*.dylib", dst="lib", src=ljs)

    def package_info(self):
        self.cpp_info.libs = ["lua51" if self.settings.compiler == "Visual Studio" else "luajit"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "dl"])
