from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os


class YASMInstallerConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = 'Yasm is a complete rewrite of the NASM assembler under the "new" BSD License'
    license = "BSD"
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = "sources"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'yasm-%s' % self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.download('https://raw.githubusercontent.com/yasm/yasm/bcc01c59d8196f857989e6ae718458c296ca20e3/YASM-VERSION-GEN.bat',
                       os.path.join('sources', 'YASM-VERSION-GEN.bat'))

    def build(self):
        if self.settings.os_build == 'Windows':
            self._build_vs()
        else:
            self._build_configure()

    def _build_vs(self):
        with tools.chdir(os.path.join(self._source_subfolder, 'Mkfiles', 'vc10')):
            with tools.vcvars(self.settings, arch=str(self.settings.arch_build), force=True):
                msbuild = MSBuild(self)
                if self.settings.arch_build == "x86":
                    msbuild.build_env.link_flags.append('/MACHINE:X86')
                elif self.settings.arch_build == "x86_64":
                    msbuild.build_env.link_flags.append('/SAFESEH:NO /MACHINE:X64')
                msbuild.build(project_file="yasm.sln", arch=self.settings.arch_build, build_type="Release",
                              targets=["yasm"], platforms={"x86": "Win32"}, force_vcvars=True)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            cc = os.environ.get('CC', 'gcc')
            cxx = os.environ.get('CXX', 'g++')
            if self.settings.arch_build == 'x86':
                cc += ' -m32'
                cxx += ' -m32'
            elif self.settings.arch_build == 'x86_64':
                cc += ' -m64'
                cxx += ' -m64'
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars.update({'CC': cc, 'CXX': cxx})
            env_build.configure(vars=env_build_vars)
            env_build.make(vars=env_build_vars)
            env_build.install(vars=env_build_vars)

    def package(self):
        self.copy(pattern="BSD.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src=self._source_subfolder, dst='bin', keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

    def package_id(self):
        del self.info.settings.compiler
