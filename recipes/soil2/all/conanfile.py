from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os


class soil2Conan(ConanFile):
    name = "soil2"
    description = "Simple OpenGL Image Library 2"
    topics = ("conan", "soil2", "opengl", "images")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SpartanJ/SOIL2"
    license = "MIT-0"
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "premake"

    def config_options(self):
        # Visual Studio users: SOIL2 will need to be compiled as C++ source ( at least the file etc1_utils.c ), since VC compiler doesn't support C99
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not tools.which("premake"):
            self.build_requires("premake/5.0.0-alpha14")
    
    def requirements(self):
        self.requires("opengl/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SOIL2-release-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def system_requirements(self):
        if self.settings.os == "Macos":
            self.run("brew install xquartz")

    def build(self):
        config = "debug" if self.settings.build_type == "Debug" else "release"
        architecture = "x86" if self.settings.arch == "x86" else "x86_64"
        with tools.chdir(self._source_subfolder):
            if self.settings.compiler == "Visual Studio":
                self.run("premake5 --os=windows vs2015")
                with tools.chdir(os.path.join("make", "windows")):
                    build_type = "release"
                    if self.settings.build_type == "Debug":
                        build_type = "debug"

                    msbuild = MSBuild(self)
                    msbuild.build("SOIL2.sln", targets=["soil2-static-lib"], platforms={"x86": "Win32"}, build_type=build_type)
            else:
                the_os = "macosx" if self.settings.os == "Macos" else "linux"
                self.run("premake5 --os={} gmake".format(the_os))
                with tools.chdir(os.path.join("make", the_os)):
                    env_build = AutoToolsBuildEnvironment(self)
                    env_build.make(args=["soil2-static-lib", "config={}".format(config + "_" + architecture) ])

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/SOIL2", src="{}/src/SOIL2/".format(self._source_subfolder))
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["soil2-debug" if self.settings.build_type == "Debug" else "soil2"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation"])
