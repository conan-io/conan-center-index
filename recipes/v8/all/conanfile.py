from conans import ConanFile, CMake, tools
import os
import shutil

class v8Conan(ConanFile):
    name = "v8"
    version = "8.2.49"
    description = "Javascript Engine"
    topics = ("javascript", "C++", "embedded", "google")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://v8.dev"
    license = "MIT"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    build_requires = [# "depot_tools_installer/master@bincrafters/stable", # does not work, bc always outdated..
                      # "GN/master@inexorgame/testing",             not needed, as its shipped with depot_tools
                      # "ninja_installer/1.8.2@bincrafters/stable", not needed, as its shipped with depot_tools
                      # "GNGenerator/0.1@inexorgame/testing" (so dependencies get picked up)
    ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _set_environment_vars(self):
        """set the environment variables, such that the google tooling is found (including the bundled python2)"""
        os.environ["PATH"] = os.path.join(self.source_folder, "depot_tools") + os.pathsep + os.environ["PATH"]
        os.environ["DEPOT_TOOLS_PATH"] = os.path.join(self.source_folder, "depot_tools")
        if tools.os_info.is_windows:
            os.environ["DEPOT_TOOLS_WIN_TOOLCHAIN"] = "0"
            if str(self.settings.compiler.version) not in ["15", "16"]:
                raise ValueError("not yet supported visual studio version used for v8 build")
            os.environ["GYP_MSVS_VERSION"] = "2017" if str(self.settings.compiler.version) == "15" else "2019"


    def source(self):
        self.run("git clone --depth 1 https://chromium.googlesource.com/chromium/tools/depot_tools.git")
        self._set_environment_vars()
        self.run("gclient")
        self.run("fetch v8")
        with tools.chdir("v8"):
            self.run("git checkout {}".format(self.version))

    @staticmethod
    def get_gn_profile(settings):
        """return the profile defined somewhere in v8/infra/mb/mb_config.pyl which corresponds "nearly" to the one we need.. "nearly" as in "not even remotely"..
        """
        return "{arch}.{build_type}".format(build_type=str(settings.build_type).lower(),
                                arch="x64" if str(settings.arch) == "x86_64" else "x86")

    def _install_system_requirements_linux(self):
        """some extra script must be executed on linux"""
        os.environ["PATH"] += os.pathsep + os.path.join(self.source_folder, "depot_tools")
        self.run("chmod +x v8/build/install-build-deps.sh")
        #self.run("v8/build/install-build-deps.sh --unsupported --no-arm --no-nacl "
        #         "--no-backwards-compatible --no-chromeos-fonts --no-prompt "
        #         + "--syms" if str(self.settings.build_type) == "Debug" else "--no-syms")

    def build(self):
        self._set_environment_vars()

        if tools.os_info.is_linux:
            self._install_system_requirements_linux()

        # fix gn always detecting the runtime on its own:
        if str(self.settings.compiler) == "Visual Studio" and str(self.settings.compiler.runtime) in ["MD", "MDd"]:
            build_gn_file = os.path.join("v8", "build", "config", "win", "BUILD.gn")
            print("replacing MT / MTd with MD / MDd in gn file." + build_gn_file)
            tools.replace_in_file(file_path=build_gn_file, search="MT", replace="MD")

        with tools.chdir("v8"):
            arguments = ["v8_monolithic = true",
                         "is_component_build = false",
                         "v8_static_library = true",
                         "treat_warnings_as_errors = false",
                         "v8_use_external_startup_data = false",
                         "v8_enable_i18n_support = true"
                        ]
            # v8_enable_backtrace=false,

            if tools.os_info.is_linux:
                arguments += ["use_sysroot = false",
                              "use_custom_libcxx = false",
                              "use_custom_libcxx_for_host = false",
                              "use_glib = false",
                              "is_clang = " + ( "true" if "clang" in str(self.settings.compiler).lower() else "false" ) ]

            generator_call = 'gn gen out.gn/x64.release --args="{gn_args}"'.format(profile=self.get_gn_profile(self.settings),
                                                                                gn_args=" ".join(arguments))
            # maybe todo: absolute path..
            if tools.os_info.is_windows:
                # this is picking up the python shipped via depot_tools, since we got it in the path.
                generator_call = "python " + generator_call
            self.run("python --version")
            self.run(generator_call)
            self.run("ninja -C out.gn/{profile} v8_monolith".format(profile=self.get_gn_profile(self.settings)))


    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src="v8")
        self.copy(pattern="*v8_monolith.a", dst="lib", keep_path=False)
        self.copy(pattern="*v8_monolith.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.h", dst="include", src="v8/include", keep_path=True)


    def package_info(self):
        # fix issue on Windows and OSx not finding the KHR files
        # self.cpp_info.includedirs.append(os.path.join("include", "MagnumExternal", "OpenGL"))
        # builtLibs = tools.collect_libs(self)
        self.cpp_info.libs = ["v8_monolith"]  # sort_libs(correct_order=allLibs, libs=builtLibs, lib_suffix=suffix, reverse_result=True)
