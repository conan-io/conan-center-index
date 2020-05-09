import os, stat, json, re, subprocess
from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
from conans.errors import ConanInvalidConfiguration
from conans.model import Generator


class VCVRackSDKConan(ConanFile):
    name = "vcvrack-sdk"
    version = "1.1.6"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://vcvrack.com"
    description = "VCV Rack SDK for Rack plugin development."

    settings = "os", "compiler", "arch"

    _SDK_DIR = "Rack-SDK"

    def configure(self):
        if self._isVisualStudioBuild:
            self.output.error("Rack SDK on Windows is only compatible with MinGW GCC toolchain!")
            raise ConanInvalidConfiguration("VCV Rack SDK is not compatible with Visual Studio!")

        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("VCV Rack SDK only supports x86_64 platform!")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires.add("msys2/20190524")

    def system_requirements(self):
        packages = ["git", "zip", "make", "cmake", "jq"]
        update_installer = True

        if self.settings.os == "Windows":
            self.output.warn("manipulate script internal environment - add MSYS_BIN to PATH for using pacman tool")
            del os.environ["CONAN_SYSREQUIRES_SUDO"]
            os.environ["PATH"] += os.pathsep + self.env["MSYS_BIN"]
            packages = ["zip", "mingw-w64-x86_64-jq", "mingw-w64-x86_64-libwinpthread"]
            update_installer = False

        if self.settings.os == "Macos":
            packages += ["autoconf", "automake", "libtool"]

        if self.settings.os == "Linux":
            mesaPackage = { "ubuntu": "libglu1-mesa-dev",
                            "debian": "libglu1-mesa-dev",
                            "fedora": "mesa-libGLU-devel",
                            "centos": "mesa-libGLU-devel",
                            "arch": "mesa"
                          }
            packages += [mesaPackage[os_info.linux_distro]]

        installer = SystemPackageTool()
        for package in packages:
            installer.install(package, update=update_installer)

    def build(self):
        tools.get(**self.conan_data["sources"][self.version])

    def package(self):
        self.copy("*.*", dst="include", src="{}/include".format(self._SDK_DIR))
        self.copy("*.*", dst="dep", src="{}/dep".format(self._SDK_DIR))
        self.copy("*.mk", dst=".", src="{}".format(self._SDK_DIR))
        os.chmod(os.path.join(self._SDK_DIR, "helper.py"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)
        self.copy("helper.py", dst="script", src="{}".format(self._SDK_DIR))
        self.copy("*Rack*.a", dst=".", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.cxxflags.append("-DARCH_WIN")
            self.cpp_info.libs.append("Rack")
            self.env_info.path.append(os.path.join(self.deps_env_info["msys2"].MSYS_ROOT, "mingw64", "bin"))
            self.cpp_info.libdirs.append(os.path.join(self.package_folder))
            self.user_info.rack_sdk_dir = os.path.join(self.package_folder)

        if self.settings.os == "Linux":
            self.cpp_info.cxxflags.append("-DARCH_LIN")

        if self.settings.os == "Macos":
            self.cpp_info.cxxflags.append("-DARCH_MAC -undefined dynamic_lookup")
        else:
            self.cpp_info.cxxflags.append("-Wsuggest-override")

        self.cpp_info.cxxflags.append("-D_USE_MATH_DEFINES -march=nocona -funsafe-math-optimizations -fPIC")
        self.cpp_info.cxxflags.append("-Wall -Wextra -Wno-unused-parameter")

        self.cpp_info.includedirs = ["include", "dep/include"]
        self.env_info.path.append(os.path.join(self.package_folder, "script"))
        self.env_info.RACK_DIR = os.path.join(self.package_folder)

    def package_id(self):
       self.info.header_only()

    @property
    def _isMinGWBuild(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _isVisualStudioBuild(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

# custom generator to generate CMakeSettings.json that can be used with MS Visual Studio
class VSCMakeSettings(Generator):

    @property
    def filename(self):
        return "CMakeSettings.json"

    @property
    def content(self):
        if self.settings.os != "Windows":
            print("*** VSCMakeSettings generator is only supported on Windows - generate empty file!")
            return "VSCMakeSettings generator is only supported on Windows!"
        print("*** Generate '{}' for Visual Studio".format(self.filename))
        print("*** Please copy the generated '{}' manually into your Plugin source folder to use it with Visual Studio!".format(self.filename))
        content = { "configurations" : [ self._createConfiguration("Release"),
                                         self._createConfiguration("Debug")
                                       ]
                  }
        return json.dumps(content, indent=2)

    def _createConfiguration(self, cmakeBuildtype):
        configuration = { "name" : "Mingw64-{}".format(cmakeBuildtype),
                          "generator": "Ninja",
                          "configurationType": cmakeBuildtype,
                          "buildRoot": "${projectDir}\\out\\build\\${name}",
                          "installRoot": "${projectDir}\\out\\install\\${name}",
                          "cmakeCommandArgs": "",
                          "buildCommandArgs": "-v",
                          "ctestCommandArgs": "",
                          "inheritEnvironments": [ "mingw_64" ],
                          "environments": [ self._createEnvironment ],
                          "variables": self._createVariables,
                          "intelliSenseMode": "linux-gcc-x64"
         }
        return configuration

    @property
    def _createEnvironment(self):
        environment = { "MINGW64_ROOT": self._getMinGWRoot,
                        "BIN_ROOT": os.path.join(self._getMinGWHome, "bin"),
                        "FLAVOR": self._getFlavor,
                        "TOOLSET_VERSION": self._getToolsetVersion,
                        "GCC_HEADERS_ROOT": "${env.MINGW64_ROOT}\\${env.FLAVOR}\\${env.TOOLSET_VERSION}\\include",
                        "PATH": "${env.BIN_ROOT};${env.PATH}",
                        "INCLUDE": "${env.INCLUDE};${env.GCC_HEADERS_ROOT}\\c++;${env.GCC_HEADERS_ROOT}\\c++\\${env.FLAVOR};${env.GCC_HEADERS_ROOT}\\c++\\backward;${env.GCC_HEADERS_ROOT}\\include;${env.GCC_HEADERS_ROOT}\\..\\include-fixed;${env.BIN_ROOT}\\..\\${env.FLAVOR}\\include",
                        "environment": "mingw_64"
                      }
        return environment

    @property
    def _getMinGWHome(self):
        return self.conanfile.deps_env_info["mingw_installer"].MINGW_HOME

    @property
    def _getMinGWRoot(self):
        return os.path.join(self._getMinGWHome, "lib", "gcc")

    def _getGccInfo(self, option):
        result = subprocess.run(os.path.join(self._getMinGWHome, "bin", "gcc.exe") + " -{}".format(option), capture_output=True)
        return result.stdout.decode('utf-8').strip()

    @property
    def _getFlavor(self):
        return self._getGccInfo("dumpmachine")

    @property
    def _getToolsetVersion(self):
        return self._getGccInfo("dumpversion")

    @property
    def _createVariables(self):
        variables = [ self._createCMakeVariable("CMAKE_C_COMPILER", "${env.BIN_ROOT}\\gcc.exe", "STRING"),
                      self._createCMakeVariable("CMAKE_CXX_COMPILER", "${env.BIN_ROOT}\\g++.exe", "STRING"),
                      self._createCMakeVariable("RACK_SDK", "{}".format(self.conanfile.deps_user_info["vcvrack-sdk"].rack_sdk_dir), "STRING")
                    ]
        return variables


    def _createCMakeVariable(self, name, value, varType):
        variable = { "name": name,
                      "value": value,
                      "type": varType
                   }
        return variable
