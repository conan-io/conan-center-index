import os
from conans import CMake, ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import shutil


class LibModbusConan(ConanFile):
    name = "libmodbus"
    license = "LGPL-2.1"
    homepage = "http://libmodbus.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = """libmodbus is a free software library to send/receive data with a device which respects the Modbus protocol."""
    topics = ("modbus")
    exports_sources = ["extra/*" , "CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            shutil.move(self.source_folder + "/CMakeLists.txt.in",
                        self.source_folder + "/{}/CMakeLists.txt".format(self._source_subfolder))
            shutil.move(self.source_folder + "/extra/win_config.h",
                        self.source_folder + "/{}/config.h".format(self._source_subfolder))
            shutil.move(self.source_folder + "/extra/project-config.cmake.in",
                        self.source_folder + "/{}/project-config.cmake.in".format(self._source_subfolder))
            tools.patch(patch_file = self.source_folder + "/extra/modbus.patch",
                        base_path=self._source_subfolder)
            cmake = CMake(self)
            cmake.configure(source_folder=self._source_subfolder, build_folder = self._build_subfolder)
            cmake.build()
            cmake.install()
        else:
            if self.options.shared:
                shared_static = "--enable-host-shared --prefix "
            else:
                shared_static = "--enable-static --disable-shared --prefix "

            # Assumes that x86 is the host os and building for e.g. armv7
            if self.settings.arch != "x86_64" or self.settings.arch != "x86":
                cross_host = "--host={} ".format(self.settings.arch)
            else:
                cross_host = ""
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True
            with tools.environment_append(env_build.vars):
                self.run("cd {} && ./autogen.sh".format(self._source_subfolder))
                self.run("cd {} && ./configure {}{}{}".format(self._source_subfolder,
                                                              cross_host,
                                                              shared_static,
                                                              self.package_folder))
                self.run("cd {} && make".format(self._source_subfolder))
                self.run("cd {} && make install".format(self._source_subfolder))

    def package(self):
        self.copy("COPYING.LESSER", dst="licenses", src=self._source_subfolder,
                  ignore_case=True, keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared == True:
                self.cpp_info.libs = ["modbus"]
            else:
                self.cpp_info.libs = ["libmodbus", "ws2_32"]
                self.cpp_info.defines = ["LIBMODBUS_STATICBUILD"]
            if self.settings.build_type == "Debug":
                self.cpp_info.libs[0] += '_d'
        else:
            self.cpp_info.libs = ["modbus"]
        self.cpp_info.includedirs = ["include"]