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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def build_requirements(self):
        self.tool_requires("cmake/[>3.23 <4]")

    def requirements(self):
        self.requires("ohnet/1.36.5182", transitive_headers=True, transitive_libs=True)
        self.requires("libressl/3.5.3")
        self.requires("libmad/0.15.1b")
        self.requires("alac/cci.20121212")
        self.requires("libfdk_aac/2.0.2")
        self.requires("faac/1.30")
        self.requires("flac/1.4.2")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")

    def layout(self):
        cmake_layout(self, src_folder="src")

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
