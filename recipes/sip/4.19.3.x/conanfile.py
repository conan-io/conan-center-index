import os
import stat
import glob
import shutil
import json
from conans import ConanFile, AutoToolsBuildEnvironment, tools

# based on https://github.com/conan-community/conan-ncurses/blob/stable/6.1/conanfile.py
class SipConan(ConanFile):
    name = "sip"
    license = "GPL2"
    homepage = "https://www.riverbankcomputing.com/software/sip/intro"
    description = "SIP comprises a code generator and a Python module"
    url = "https://www.riverbankcomputing.com/hg/sip"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "python": ['python2', 'python3'],
    }
    default_options = {
        "python": "python2",
    }
    exports = ""
    _source_subfolder = "source_subfolder"

    @property
    def original_version(self):
        if 'dssl' in self.version:
            v = self.version.split('.')
            return '.'.join(v[:-1])
        return self.version

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_apt:
                packages = []
                if self.options.python == "python3":
                    packages.append( "python3-dev" )
                else:
                    if ((tools.os_info.linux_distro == "ubuntu" and tools.os_info.os_version < "20") or
                        (tools.os_info.linux_distro == "debian" and tools.os_info.os_version < "11")):
                        packages.append( "python-dev")
                    else:
                        packages.append( "python2-dev" )
            else:
                self.output.warn("Do not know how to install Python headers for {}-{}.".format(
                    tools.os_info.linux_distro, tools.os_info.os_version)
                )

        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self)
            package_tool.install_packages(update=True, packages=packages)

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.22")
        if tools.os_info.is_macos or tools.os_info.is_linux:
            self.build_requires("bison/3.5.3")
            self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.original_version])
        extracted_folder = "sip-" + self.original_version
        os.rename(extracted_folder, self._source_subfolder)

        if tools.os_info.is_windows:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "build.py"),
                "os.system('flex",
                "os.system('win_flex"
            )
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "build.py"),
                "os.system('bison",
                "os.system('win_bison"
            )

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{python} build.py prepare".format(python = self.options.python))
            if tools.os_info.is_macos or tools.os_info.is_linux:
                if tools.os_info.is_macos:
                    cfg = ("{python} configure.py"
                        + " --deployment-target=10.12"
                        + " -b {prefix}/bin"
                        + " -d {prefix}/lib-dynload"
                        + " -e {prefix}/include"
                        + " -v {prefix}/share/sip")
                if tools.os_info.is_linux:
                    cfg = ("{python} configure.py"
                        + " -b {prefix}/bin"
                        + " -d {prefix}/site-packages"
                        + " -e {prefix}/include"
                        + " -v {prefix}/share/sip")
                self.run(cfg.format(
                    prefix = tools.unix_path(self.package_folder),
                    python = self.options.python
                ))
                self.run("make -j%d" % tools.cpu_count())
            if tools.os_info.is_windows:
                self.run(("{python} configure.py"
                    + " -b {prefix}/bin"
                    + " -d {prefix}/site-packages"
                    + " -e {prefix}/include"
                    + " -v {prefix}/share/sip"
                ).format(
                    prefix = self.package_folder,
                    python = self.options.python
                ))
                # cannot be bothered to fix build of siplib which we don't use anyway
                vcvarsall_cmd = tools.vcvars_command(self)
                with tools.chdir("sipgen"):
                    self.run("{vcv} && nmake".format(vcv=vcvarsall_cmd))

    def package(self):
        if tools.os_info.is_macos or tools.os_info.is_linux:
            with tools.chdir(self._source_subfolder):
                self.run("make install")
        elif tools.os_info.is_windows:
            with tools.chdir(self._source_subfolder):
                # partial execution of installation step due to siplib not being built
                with tools.chdir("sipgen"):
                    vcvarsall_cmd = tools.vcvars_command(self)
                    self.run("{vcv} && nmake install".format(vcv=vcvarsall_cmd))
                with tools.chdir("siplib"):
                    self.run("mkdir {prefix}\\include\\".format(prefix = self.package_folder))
                    self.run("copy /y sip.h {prefix}\\include\\sip.h".format(prefix = self.package_folder))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = ["include"]
        if tools.os_info.is_macos:
            self.cpp_info.libdirs = ["lib-dynload"]
        if tools.os_info.is_linux:
            self.cpp_info.libdirs = ["site-packages"]
