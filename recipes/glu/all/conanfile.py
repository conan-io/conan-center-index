from conans import ConanFile, tools
from conans.errors import ConanException
import os

class SysConfigGLUConan(ConanFile):
    name = "glu"
    version = "system"
    description = "cross-platform virtual conan package for the GLU support"
    topics = ("conan", "opengl", "glu")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.opengl.org/"
    license = "MIT"
    settings = ("os",)

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("GLU development files aren't available, give up")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.system_libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_dirs)
        self.cpp_info.sharedlinkflags.extend(ldflags)
        self.cpp_info.exelinkflags.extend(ldflags)
        self.cpp_info.defines.extend(defines)
        self.cpp_info.includedirs.extend(include_dirs)
        self.cpp_info.cflags.extend(cflags)
        self.cpp_info.cxxflags.extend(cflags)

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            if tools.os_info.with_yum:
                packages = ["mesa-libGLU-devel"]
            elif tools.os_info.with_apt:
                packages = ["libglu1-mesa-dev"]
            elif tools.os_info.with_pacman:
                packages = ["glu"]
            elif tools.os_info.with_zypper:
                packages = ["Mesa-libGLU-devel"]
            else:
                self.warn("don't know how to install OpenGL for your distro")
            package_tool.install(update=True, packages=packages)
    
    def package_info(self):
        if self.settings.os == "Macos":
            self.cpp_info.defines.append("GL_SILENCE_DEPRECATION=1")
            self.cpp_info.frameworks.append("OpenGL")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Glu32"]
        elif self.settings.os == "Linux":
            self._fill_cppinfo_from_pkgconfig("glu")
