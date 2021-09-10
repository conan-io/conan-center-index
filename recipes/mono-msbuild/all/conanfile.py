from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools, RunEnvironment
from conans.errors import ConanInvalidConfiguration
import glob
import os
import yaml

required_conan_version = ">=1.33.0"


class MonoConan(ConanFile):
    name = "mono-msbuild"
    description = "The Microsoft Build Engine (MSBuild) is the build platform for .NET and Visual Studio."
    url = "https://github.com/mono/mono"
    homepage = "https://github.com/mono/msbuild"
    license = "MIT, BSD"
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    topics = "mono", "dotnet"

    requires = ["mono/6.12.0.122"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        os.mkdir(self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            git = tools.Git()
            git.clone(url="https://github.com/mono/msbuild.git")
            # latest commit on xplat-master as of 10Sep2021 (corresponds to version 16.10.1)
            git.checkout("63458bd6cb3a98b5a062bb18bd51ffdea4aa3001")

    def build(self):
        env_build = RunEnvironment(self)
        env_build.vars["HOME"] = os.path.join(self.build_folder, "homedir")
        with tools.environment_append(env_build.vars):
            with tools.chdir(self._source_subfolder):
                # Got some ideas from here:
                # https://github.com/mono/linux-packaging-msbuild/blob/main/debian/rules
                self.run("./eng/cibuild_bootstrapped_msbuild.sh --host_type mono --configuration Release --skip_tests /p:DisableNerdbankVersioning=true")
                self.run("/bin/bash ./stage1/mono-msbuild/msbuild mono/build/install.proj /p:MonoInstallPrefix={} /p:Configuration=Release-MONO /p:IgnoreDiffFailure=true".format(
                    os.path.join(self.build_folder, "tmp", "usr")))

    def package(self):
        # replace absolute path for mono in msbuild script with empty string to use the mono binary from conan package
        self.output.info('sed -i "s@{0}/tmp/usr/bin/@@g" {0}/tmp/usr/bin/msbuild'.format(self.build_folder))
        self.run('sed -i "s@{0}/tmp/usr/bin/@@g" {0}/tmp/usr/bin/msbuild'.format(self.build_folder))
        # replace absolute path to libs in msbuild with MSBUILD_ROOT_DIR environment variable
        self.output.info('sed -i "s@{0}/tmp/usr/lib@{1}/lib@g" {0}/tmp/usr/bin/msbuild'.format(self.build_folder, "\\${MSBUILD_ROOT_DIR}"))
        self.run('sed -i "s@{0}/tmp/usr/lib@{1}/lib@g" {0}/tmp/usr/bin/msbuild'.format(self.build_folder, "\\${MSBUILD_ROOT_DIR}"))
        tools.remove_files_by_mask(os.path.join(self.build_folder,"tmp", "usr", "lib", "mono"), "Microsoft.DiaSymReader.Native.*dll")
        tools.remove_files_by_mask(os.path.join(self.build_folder,"tmp", "usr", "lib", "mono"), "System.Reflection.Metadata.dll")
        tools.remove_files_by_mask(os.path.join(self.build_folder,"tmp", "usr", "lib", "mono"), "*.dylib")
        tools.remove_files_by_mask(os.path.join(self.build_folder,"tmp", "usr", "lib", "mono"), "*.so")
        tools.remove_files_by_mask(os.path.join(self.build_folder,"tmp", "usr", "lib", "mono"), "*.so")
        # See https://github.com/mono/linux-packaging-msbuild/blob/main/debian/msbuild.install
        self.copy("*", dst="bin", src=os.path.join("tmp", "usr", "bin"))
        self.copy("*", dst=os.path.join("lib", "mono"), src=os.path.join("tmp", "usr", "lib", "mono"))


    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "msbuild"
        self.cpp_info.names["cmake_find_package_multi"] = "msbuild"
        self.cpp_info.names["pkg_config"] = "msbuild"
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.MSBUILD_ROOT_DIR = self.package_folder

