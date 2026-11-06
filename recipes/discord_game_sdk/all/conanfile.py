import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0"


class DiscordGameSdkConan(ConanFile):
    name = "discord_game_sdk"
    description = "The Discord GameSDK is an easy drop-in SDK to help you manage all the hard things that come with making a game."
    license = "LicenseRef-discord-game-sdk" # https://discord.com/developers/docs/legal
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://discord.com/developers/docs/game-sdk/sdk-starter-guide"
    topics = ("discord", "game", "sdk", "gamedev")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _sdk_lib_arch(self):
        arch = str(self.settings.arch)
        if arch == "x86":
            return "x86"
        elif arch == "x86_64":
            return "x86_64"
        elif arch.startswith("armv8"):
            return "aarch64"
        return None

    @property
    def _sdk_lib_dir(self):
        return os.path.join(self.source_folder, "lib", self._sdk_lib_arch)

    def validate(self):
        os_name = str(self.settings.os)
        arch_name = str(self.settings.arch)
        supported = (
            (os_name == "Windows" and arch_name in ("x86", "x86_64")) or
            (os_name == "Linux" and arch_name == "x86_64") or
            (os_name == "Macos" and arch_name in ("x86_64", "armv8"))
        )
        if not supported:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {os_name}/{arch_name}"
            )
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=False)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDK_LIB_FOLDER"] = self._sdk_lib_dir.replace("\\", "/")
        tc.generate()

    def build(self):
        if self.settings.os == "Windows":
            rename(self, os.path.join(self._sdk_lib_dir, "discord_game_sdk.dll.lib"),
                   os.path.join(self._sdk_lib_dir, "discord_game_sdk.lib"))
        elif self.settings.os == "Macos":
            rename(self, os.path.join(self._sdk_lib_dir, "discord_game_sdk.dylib"),
                   os.path.join(self._sdk_lib_dir, "libdiscord_game_sdk.dylib"))
        else:
            rename(self, os.path.join(self._sdk_lib_dir, "discord_game_sdk.so"),
                   os.path.join(self._sdk_lib_dir, "libdiscord_game_sdk.so"))

        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_folder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows":
            copy(self, "discord_game_sdk.dll", src=self._sdk_lib_dir,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "discord_game_sdk.lib", src=self._sdk_lib_dir,
                 dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        elif self.settings.os == "Macos":
            copy(self, "libdiscord_game_sdk.dylib", src=self._sdk_lib_dir,
                 dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            copy(self, "libdiscord_game_sdk.so", src=self._sdk_lib_dir,
                 dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["discord_game_sdk_cpp", "discord_game_sdk"]
        if self.settings.os == "Windows":
            self.cpp_info.bindirs = ["bin"]
