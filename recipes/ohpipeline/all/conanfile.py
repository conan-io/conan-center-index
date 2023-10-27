from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.53.0"


class OhPipelineConan(ConanFile):
    name = "ohpipeline"
    description = "OpenHome audio pipeline"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openhome/ohPipeline"
    topics = ("openhome", "ohnet", "ohpipeline", "upnp")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def _get_openhome_architecture(self, args):
        if is_apple_os(self):
            if str(self.settings.arch).startswith("armv8"):
                openhome_architecture = "arm64"
                args.extend([f"openhome_architecture={openhome_architecture}", f"detected_openhome_architecture={openhome_architecture}"])
        return args

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def requirements(self):
        self.requires("ohnet/1.36.5182", transitive_headers=True, transitive_libs=True)
        self.requires("libressl/3.5.3", transitive_headers=True, transitive_libs=True)
        self.requires("libmad/0.15.1b", transitive_headers=True, transitive_libs=True)
        self.requires("alac/cci.20121212", transitive_headers=True, transitive_libs=True)
        self.requires("libfdk_aac/2.0.2", transitive_headers=True, transitive_libs=True)
        self.requires("faac/1.30", transitive_headers=True, transitive_libs=True)
        self.requires("flac/1.4.2", transitive_headers=True, transitive_libs=True)
        self.requires("ogg/1.3.5", transitive_headers=True, transitive_libs=True)
        self.requires("vorbis/1.3.7", transitive_headers=True, transitive_libs=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = [
            "ohPipeline",
            "ohMediaPlayer",
            "Odp",
            "SourcePlaylist",
            "SourceRadio",
            "SourceSongcast",
            "SourceScd",
            "SourceRaop",
            "SourceUpnpAv",
            "Podcast",
            "ScdSender",
            "CodecWav",
            "CodecPcm",
            "CodecDsdDsf",
            "CodecDsdDff",
            "CodecDsdRaw",
            "CodecAiffBase",
            "CodecAifc",
            "CodecAiff",
            "CodecFlac",
            "CodecAlacAppleBase",
            "CodecAlacApple",
            "CodecAacFdkBase",
            "CodecAacFdkMp4",
            "CodecAacFdkAdts",
            "CodecMp3",
            "CodecVorbis",
            "WebAppFramework",
            "WebAppFrameworkTestUtils",
            "ConfigUi",
            "ConfigUiTestUtils",
        ]
