from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

class IceoryxConan(ConanFile):

    name = "iceoryx"
    license = "Apache-2.0"
    homepage = "https://iceoryx.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse iceoryx - true zero-copy inter-process-communication"
    topics = ("Shared Memory", "IPC", "ROS", "Middleware")
    settings = "os", "compiler", "build_type", "arch"
    options = {
         "shared":          [True, False],
         "toml_config":     [True, False]
    }
    default_options = {
        "shared":           False,
        "toml_config":      True
    }
    generators = ["cmake", "cmake_find_package"]
    exports_sources = ["patches/**","CMakeLists.txt"]
    _cmake = None

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, alias, aliased):
        content = ""
        content += textwrap.dedent("""\
            if(TARGET {aliased} AND NOT TARGET {alias})
                add_library({alias} INTERFACE IMPORTED)
                set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
            endif()
        """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join(
            "lib",
            "cmake"
        )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_folder(self):
        return "build"

    @property
    def _pkg_share(self):
        return os.path.join(
            self.package_folder,
            "share"
        )

    @property
    def _pkg_etc(self):
        return os.path.join(
            self.package_folder,
            "etc"
        )
    
    @property
    def _pkg_res(self):
        return os.path.join(
            self.package_folder,
            "res"
        )

    @property
    def _pkg_cmake(self):
        return os.path.join(
            self.package_folder,
            "lib/cmake"
        )

    @property
    def _target_aliases(self):
        return {
            "iceoryx_posh::iceoryx_posh": "iceoryx::posh",
            "iceoryx_posh::iceoryx_posh_roudi": "iceoryx::posh_roudi",
            "iceoryx_binding_c::iceoryx_binding_c": "iceoryx::binding_c",
            "iceoryx_utils::iceoryx_utils": "iceoryx::utils"
        }

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def config_options(self):
        if self.options.toml_config:
            self.requires("cpptoml/0.1.1")
        if self.settings.os == "Linux":
            self.requires("acl/2.3.1")
    
    def validate(self):
        os = self.settings.os
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                'Using Iceoryx on Windows currently just possible with "shared=False"')
        if (compiler == "gcc" or compiler == "clang") and compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                'Using Iceoryx with gcc or clang on Linux requires "compiler.libcxx=libstdc++11"')
        if os == "Linux" and compiler == "gcc" and version <= "5":
            raise ConanInvalidConfiguration(
                "Using Iceoryx with gcc on Linux requires gcc 6 or higher.")
        if os == "Linux" and compiler == "gcc" and version == "6":
            self.output.warn(
                "Iceoryx package is compiled with gcc 6, it is recommended to use 7 or higher")
            self.output.warn(
                "GCC 6 will built with warnings.")
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(
                "Iceoryx is just supported for Visual Studio compiler 16 and higher.")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TOML_CONFIG"] = self.options.toml_config
        self._cmake.configure()
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(self._pkg_share)
        tools.rmdir(self._pkg_cmake)
        tools.mkdir(self._pkg_res)
        if self.options.toml_config:
            tools.rename(
                os.path.join(self._pkg_etc, "roudi_config_example.toml"),
                os.path.join(self._pkg_res, "roudi_config.toml")
            )
        tools.rmdir(self._pkg_etc)
        for alias, aliased in self._target_aliases.items():
            cmake_file = "conan-official-{}-targets.cmake".format(
                aliased.replace("::", "_")
            )
            self._create_cmake_module_alias_targets(
                os.path.join(
                    self.package_folder,
                    self._module_subfolder,
                    cmake_file
                ),
                alias,
                aliased
            )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "iceoryx"
        self.cpp_info.names["cmake_find_multi_package"] = "iceoryx"
        # platform component
        self.cpp_info.components["platform"].name = "platform"
        self.cpp_info.components["platform"].libs = ["iceoryx_platform"]
        if self.settings.os in ["Linux","Macos","Neutrino"]:
            self.cpp_info.components["platform"].system_libs.append("pthread")
        # utils component
        self.cpp_info.components["utils"].name = "utils"
        self.cpp_info.components["utils"].libs = ["iceoryx_utils"]
        self.cpp_info.components["utils"].requires = ["platform"]
        if self.settings.os == "Linux":
            self.cpp_info.components["utils"].requires.append("acl::acl")
            self.cpp_info.components["utils"].system_libs.append("rt")
        if self.settings.os in ["Linux","Macos","Neutrino"]:
            self.cpp_info.components["utils"].system_libs.append("pthread")
        if self.settings.os == "Linux":
            self.cpp_info.components["utils"].system_libs.append("atomic")
        self.cpp_info.components["utils"].builddirs = self._pkg_cmake
        self.cpp_info.components["utils"].build_modules["cmake_find_package"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_utils-targets.cmake")
        ]
        self.cpp_info.components["utils"].build_modules["cmake_find_package_multi"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_utils-targets.cmake")
        ]
        # posh component 
        self.cpp_info.components["posh"].name = "posh"
        self.cpp_info.components["posh"].libs = ["iceoryx_posh"]
        self.cpp_info.components["posh"].requires = ["utils"]
        if self.settings.os in ["Linux","Macos","Neutrino"]:
            self.cpp_info.components["posh"].system_libs.append("pthread")
        self.cpp_info.components["posh"].builddirs = self._pkg_cmake
        self.cpp_info.components["posh"].build_modules["cmake_find_package"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_posh-targets.cmake")
        ]
        self.cpp_info.components["posh"].build_modules["cmake_find_package_multi"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_posh-targets.cmake")
        ]
        # roudi component
        self.cpp_info.components["posh_roudi"].name = "posh_roudi"
        self.cpp_info.components["posh_roudi"].libs = ["iceoryx_posh_roudi"]
        self.cpp_info.components["posh_roudi"].requires = ["utils", "posh"]
        if self.options.toml_config:
            self.cpp_info.components["post_roudi"].requires.append("cpptoml::cpptoml")
        if self.settings.os in ["Linux","Macos","Neutrino"]:
            self.cpp_info.components["posh_roudi"].system_libs.append("pthread")
        self.cpp_info.components["posh_roudi"].builddirs = self._pkg_cmake
        self.cpp_info.components["posh_roudi"].build_modules["cmake_find_package"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_posh_roudi-targets.cmake")
        ]
        self.cpp_info.components["posh_roudi"].build_modules["cmake_find_package_multi"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_posh_roudi-targets.cmake")
        ]
        # posh config component 
        self.cpp_info.components["posh_config"].name = "posh_config"
        self.cpp_info.components["posh_config"].libs = ["iceoryx_posh_config"]
        self.cpp_info.components["posh_config"].requires = ["posh_roudi", "utils", "posh"]
        if self.settings.os in ["Linux","Macos","Neutrino"]:
            self.cpp_info.components["posh_config"].system_libs.extend(["pthread"])
        # posh gw component
        self.cpp_info.components["posh_gw"].name = "posh_gw"
        self.cpp_info.components["posh_gw"].libs = ["iceoryx_posh_gateway"]
        self.cpp_info.components["posh_gw"].requires = ["utils", "posh"]
        # bind_c component
        self.cpp_info.components["bind_c"].name = "binding_c"
        self.cpp_info.components["bind_c"].libs = ["iceoryx_binding_c"]
        self.cpp_info.components["bind_c"].requires = ["utils", "posh"]
        if self.settings.os in ["Linux","Macos","Neutrino"]:        
            self.cpp_info.components["bind_c"].system_libs.extend(["pthread", "stdc++"])
        self.cpp_info.components["bind_c"].builddirs = self._pkg_cmake
        self.cpp_info.components["bind_c"].build_modules["cmake_find_package"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_binding_c-targets.cmake")
        ]
        self.cpp_info.components["bind_c"].build_modules["cmake_find_package_multi"] = [
            os.path.join(self._module_subfolder, "conan-official-iceoryx_binding_c-targets.cmake")
        ]
