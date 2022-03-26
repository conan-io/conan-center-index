import os
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"

class NativefiledialogConan(ConanFile):
    name = "nativefiledialog"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mlabbe/nativefiledialog"
    description = "A tiny, neat C library that portably invokes native file open and save dialogs."
    topics = ("dialog", "gui")
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],

        "linux_backend": ["gtk3", "zenity"],
    }
    default_options = {
        "fPIC": True,
        "shared": False,

        "linux_backend": "gtk3",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os in ["Windows", "Macos"]:
            del self.options.linux_backend

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.shared:
            del self.options.fPIC

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("nativefiledialog currently does not support shared library on Windows properly due to a lack of __declspec(dllexport) declaractions. As the result, this combination is disabled.")

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("architecture %s is not supported" % self.settings.arch)

    def requirements(self):
        if self.settings.os == "Linux" and self.options.linux_backend == "gtk3":
            self.requires("gtk/3.24.24")

    def build_requirements(self):
        self.tool_requires("premake/5.0.0-alpha15")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            generator = "vs" + {"16": "2019",
                                "15": "2017",
                                "14": "2015",
                                "12": "2013",
                                "11": "2012",
                                "10": "2010",
                                "9": "2008",
                                "8": "2005"}.get(str(self.settings.compiler.version))
        else:
            generator = "gmake2"
        subdir = os.path.join(self._source_subfolder, "build", "subdir")
        os.makedirs(subdir)
        with tools.chdir(subdir):
            os.rename(os.path.join("..", "premake5.lua"), "premake5.lua")

            compile_flags = []
            if self.options.shared:
                tools.replace_in_file("premake5.lua", "StaticLib", "SharedLib")
            elif self.options.get_safe("fPIC"):
                compile_flags.append("-fPIC")

            cli = ["premake5"]
            cli.append(generator)
            if self.settings.os == "Linux":
                cli.append("--linux_backend=%s" % self.options.linux_backend)
            with tools.environment_append({"CCFLAGS": compile_flags, "CXXFLAGS": compile_flags}):
                self.run(" ".join(cli))

            if self.settings.compiler == "Visual Studio":
                msbuild = MSBuild(self)
                msbuild.build("NativeFileDialog.sln", targets=["nfd"])
            else:
                config = "debug" if self.settings.build_type == "Debug" else "release"
                config += "_x86" if self.settings.arch == "x86" else "_x64"
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=["nfd", "config=%s" % config])

    def package(self):
        for suffix in ["lib", "a", "so", "dylib"]:
            self.copy("*.%s" % suffix, dst="lib", src=os.path.join(self._source_subfolder, "build", "lib"), keep_path=False)
        for suffix in ["dll"]:
            self.copy("*.%s" % suffix, dst="bin", src=os.path.join(self._source_subfolder, "build", "lib"), keep_path=False)
        self.copy("*nfd.h", dst="include", src=self._source_subfolder, keep_path=False)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
