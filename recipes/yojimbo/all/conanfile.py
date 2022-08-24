import os
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import yaml


class YojimboConan(ConanFile):
    name = "yojimbo"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/networkprotocol/yojimbo"
    topics = ("conan", "yojimbo", "game", "udp", "protocol", "client-server", "multiplayer-game-server")
    description = "A network library for client/server games written in C++"
    license = "BSD-3-Clause"
    exports = "submoduledata.yml"
    build_requires = "premake/5.0.0-alpha15"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only 64-bit architecture supported")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("libsodium/1.0.18")
        self.requires("mbedtls/2.25.0")
 
    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        
        submodule_filename = os.path.join(self.recipe_folder, 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                submodule_data = {
                    "url": submodule["url"],
                    "sha256": submodule["sha256"],
                    "destination": os.path.join(self._source_subfolder, submodule["destination"]),
                    "strip_root": True
                }

                tools.files.get(self, **submodule_data)
                submodule_source = os.path.join(self._source_subfolder, path)
                tools.rmdir(submodule_source)

    def build(self):

        # Before building we need to make some edits to the premake file to build using conan dependencies rather than local/bundled

        # Generate the list of dependency include and library paths as strings
        include_path_str = ', '.join('"{0}"'.format(p) for p in self.deps_cpp_info["libsodium"].include_paths + self.deps_cpp_info["mbedtls"].include_paths)
        lib_path_str = ', '.join('"{0}"'.format(p) for p in self.deps_cpp_info["libsodium"].lib_paths + self.deps_cpp_info["mbedtls"].lib_paths)

        premake_path = os.path.join(self._source_subfolder, "premake5.lua")

        if self.settings.os == "Windows":
        
            # Replace Windows directory seperator
            include_path_str = include_path_str.replace("\\", "/")
            lib_path_str = lib_path_str.replace("\\", "/")
            
            # Edit the premake script to use conan rather than bundled dependencies
            tools.replace_in_file(premake_path, "includedirs { \".\", \"./windows\"", "includedirs { \".\", %s" % include_path_str, strict=True)
            tools.replace_in_file(premake_path, "libdirs { \"./windows\" }", "libdirs { %s }" % lib_path_str, strict=True)
            
            # Edit the premake script to change the name of libsodium
            tools.replace_in_file(premake_path, "\"sodium\"", "\"libsodium\"", strict=True)
            
        else:
        
        	# Edit the premake script to use  conan rather than local dependencies
            tools.replace_in_file(premake_path, "\"/usr/local/include\"", include_path_str, strict=True)
            
            
        # Build using premake
            
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

        with tools.chdir(self._source_subfolder):
            self.run("premake5 %s" % generator)
            
            if self.settings.compiler == "Visual Studio":
                msbuild = MSBuild(self)
                msbuild.build("Yojimbo.sln")
            else:
                config = "debug" if self.settings.build_type == "Debug" else "release"
                config += "_x64"
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=["config=%s" % config])


    def package(self):
        self.copy(pattern="LICENCE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="yojimbo.h", dst="include", src=self._source_subfolder)
        
        self.copy(pattern="*/yojimbo.lib", dst="lib", keep_path=False)
        self.copy(pattern="*/libyojimbo.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
