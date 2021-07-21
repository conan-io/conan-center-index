from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class IceoryxConan(ConanFile):

    name = "iceoryx"
    license = "Apache-2.0"
    homepage = "https://iceoryx.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse iceoryx - true zero-copy inter-process-communication"
    topics = ("Shared Memory", "IPC", "ROS", "Middleware")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "toml_config": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "toml_config": True,
    }
    generators = ["cmake", "cmake_find_package"]
    exports_sources = ["patches/**","CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.toml_config:
            self.requires("cpptoml/0.1.1")
        if self.settings.os == "Linux":
            self.requires("acl/2.3.1")

    def validate(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)

        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        if compiler == "Visual Studio":
            if version < "16":
                raise ConanInvalidConfiguration("Iceoryx is just supported for Visual Studio 2019 and higher.")
            if self.options.shared:
                raise ConanInvalidConfiguration('Using Iceoryx with Visual Studio currently just possible with "shared=False"')
        if compiler == "gcc":
            if version < "6":
                raise ConanInvalidConfiguration("Using Iceoryx with gcc requires gcc 6 or higher.")
            if version < "9" and compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("{} {} with {} not supported".format(compiler, version, compiler.libcxx))
            if version == "6":
                self.output.warn("Iceoryx package is compiled with gcc 6, it is recommended to use 7 or higher")
                self.output.warn("GCC 6 will build with warnings.")
        if compiler == "clang":
            if version == "7.0" and compiler.get_safe("libcxx") == "libc++" and \
               self.settings.build_type == "Debug" and self.options.shared:
                raise ConanInvalidConfiguration("{} {} with {} in {} mode not supported".format(
                                                compiler, version, compiler.libcxx, self.settings.build_type))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Honor fPIC option
        for cmake_file in [
            os.path.join("iceoryx_binding_c", "CMakeLists.txt"),
            os.path.join("iceoryx_posh", "CMakeLists.txt"),
            os.path.join("iceoryx_utils", "CMakeLists.txt"),
        ]:
            tools.replace_in_file(os.path.join(self._source_subfolder, cmake_file),
                                  "POSITION_INDEPENDENT_CODE ON", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TOML_CONFIG"] = self.options.toml_config
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.mkdir(self._pkg_res)
        if self.options.toml_config:
            tools.rename(
                os.path.join(self._pkg_etc, "roudi_config_example.toml"),
                os.path.join(self._pkg_res, "roudi_config.toml")
            )
        tools.rmdir(self._pkg_etc)
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            self._target_aliases
        )

    @property
    def _pkg_etc(self):
        return os.path.join(self.package_folder, "etc")

    @property
    def _pkg_res(self):
        return os.path.join(self.package_folder, "res")

    @property
    def _target_aliases(self):
        return {
            "iceoryx_utils::iceoryx_platform": "iceoryx::iceoryx_platform",
            "iceoryx_utils::iceoryx_utils": "iceoryx::iceoryx_utils",
            "iceoryx_posh::iceoryx_posh": "iceoryx::iceoryx_posh",
            "iceoryx_posh::iceoryx_posh_roudi": "iceoryx::iceoryx_posh_roudi",
            "iceoryx_posh::iceoryx_posh_gateway": "iceoryx::iceoryx_posh_gateway",
            "iceoryx_posh::iceoryx_posh_config": "iceoryx::iceoryx_posh_config",
            "iceoryx_binding_c::iceoryx_binding_c": "iceoryx::iceoryx_binding_c",
        }

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        # FIXME: We should provide 3 CMake config files:
        #        iceoryx_utilsConfig.cmake, iceoryx_poshConfig.cmake and iceoryx_binding_cConfig.cmake
        #        It's not possible yet, see https://github.com/conan-io/conan/issues/9000
        self.cpp_info.names["cmake_find_package"] = "iceoryx"
        self.cpp_info.names["cmake_find_multi_package"] = "iceoryx"
        # platform component
        self.cpp_info.components["iceoryx_platform"].names["cmake_find_package"] = "iceoryx_platform"
        self.cpp_info.components["iceoryx_platform"].names["cmake_find_package_multi"] = "iceoryx_platform"
        self.cpp_info.components["iceoryx_platform"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_platform"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_platform"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_platform"].libs = ["iceoryx_platform"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_platform"].system_libs.append("pthread")
        # iceoryx_utils component
        self.cpp_info.components["iceoryx_utils"].names["cmake_find_package"] = "iceoryx_utils"
        self.cpp_info.components["iceoryx_utils"].names["cmake_find_package_multi"] = "iceoryx_utils"
        self.cpp_info.components["iceoryx_utils"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_utils"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_utils"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_utils"].libs = ["iceoryx_utils"]
        self.cpp_info.components["iceoryx_utils"].requires = ["iceoryx_platform"]
        if self.settings.os == "Linux":
            self.cpp_info.components["iceoryx_utils"].requires.append("acl::acl")
            self.cpp_info.components["iceoryx_utils"].system_libs.extend(["atomic", "rt"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_utils"].system_libs.append("pthread")
        # iceoryx_posh component
        self.cpp_info.components["iceoryx_posh"].names["cmake_find_package"] = "iceoryx_posh"
        self.cpp_info.components["iceoryx_posh"].names["cmake_find_package_multi"] = "iceoryx_posh"
        self.cpp_info.components["iceoryx_posh"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_posh"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh"].libs = ["iceoryx_posh"]
        self.cpp_info.components["iceoryx_posh"].requires = ["iceoryx_utils"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_posh"].system_libs.append("pthread")
        # iceoryx_posh_roudi component
        self.cpp_info.components["iceoryx_posh_roudi"].names["cmake_find_package"] = "iceoryx_posh_roudi"
        self.cpp_info.components["iceoryx_posh_roudi"].names["cmake_find_package_multi"] = "iceoryx_posh_roudi"
        self.cpp_info.components["iceoryx_posh_roudi"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_posh_roudi"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_roudi"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_roudi"].libs = ["iceoryx_posh_roudi"]
        self.cpp_info.components["iceoryx_posh_roudi"].requires = ["iceoryx_utils", "iceoryx_posh"]
        if self.options.toml_config:
            self.cpp_info.components["iceoryx_post_roudi"].requires.append("cpptoml::cpptoml")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_posh_roudi"].system_libs.append("pthread")
        # iceoryx_posh_gateway component
        self.cpp_info.components["iceoryx_posh_gateway"].names["cmake_find_package"] = "iceoryx_posh_gateway"
        self.cpp_info.components["iceoryx_posh_gateway"].names["cmake_find_package_multi"] = "iceoryx_posh_gateway"
        self.cpp_info.components["iceoryx_posh_gateway"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_posh_gateway"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_gateway"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_gateway"].libs = ["iceoryx_posh_gateway"]
        self.cpp_info.components["iceoryx_posh_gateway"].requires = ["iceoryx_utils", "iceoryx_posh"]
        # iceoryx_posh_config component
        self.cpp_info.components["iceoryx_posh_config"].names["cmake_find_package"] = "iceoryx_posh_config"
        self.cpp_info.components["iceoryx_posh_config"].names["cmake_find_package_multi"] = "iceoryx_posh_config"
        self.cpp_info.components["iceoryx_posh_config"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_posh_config"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_config"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_posh_config"].libs = ["iceoryx_posh_config"]
        self.cpp_info.components["iceoryx_posh_config"].requires = ["iceoryx_posh_roudi", "iceoryx_utils", "iceoryx_posh"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_posh_config"].system_libs.append("pthread")
        # bind_c component
        self.cpp_info.components["iceoryx_binding_c"].names["cmake_find_package"] = "iceoryx_binding_c"
        self.cpp_info.components["iceoryx_binding_c"].names["cmake_find_package_multi"] = "iceoryx_binding_c"
        self.cpp_info.components["iceoryx_binding_c"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["iceoryx_binding_c"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_binding_c"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["iceoryx_binding_c"].libs = ["iceoryx_binding_c"]
        self.cpp_info.components["iceoryx_binding_c"].requires = ["iceoryx_utils", "iceoryx_posh"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["iceoryx_binding_c"].system_libs.append("pthread")
        libcxx = tools.stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["iceoryx_binding_c"].system_libs.append(libcxx)

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
