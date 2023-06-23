#!/usr/bin/env python

import fileinput
from conan import ConanFile
from conan.tools.files import chdir, copy, get
import os

#required_conan_version = ">=2.0.0"

class LibWebRTCConan(ConanFile):
    name = 'libwebrtc'
    description = "WebRTC C++ wrapper A C++ binary wrapper for webrtc, mainly used for flutter-webrtc desktop (windows, linux, embedded) version release."
    homepage = "https://github.com/webrtc-sdk/libwebrtc"
    license = 'Apache License 2.0'
    topics = ("webrtc")

    settings = 'os', 'build_type', 'arch'
    options = {
        "use_h264": [True, False],
    }

    default_options = {
        "use_h264": True,
    }
    
    generators = [ "CMakeDeps" ]

    depot_tools_repository = 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
    depot_tools_release = '1b72044e33798aa3c5144d609dab8ff65dac0247'
    depot_tools_dir = 'depot_tools'
    
    webrtc_release = 'm104'
    webrtc_dir = 'src'


    def source(self):
        destination_path = os.path.join(os.path.sep, self.source_folder, self.webrtc_dir, self.name)
        get(self, **self.conan_data["sources"][self.version], destination=destination_path, strip_root=True)

        self.run(f'git clone {self.depot_tools_repository} {self.depot_tools_dir}')


    def export_sources(self):
        pass


    def _set_depot_tools_environment_variables(self):
        depot_tools_path = os.path.join(os.path.sep, self.build_folder, self.depot_tools_dir)
        os.environ['PATH'] += os.pathsep + depot_tools_path
        os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'


    def _setup_depot_tools(self):
        # gclient has to be called twice, on windows if it's called once, 
        # after a switch to specified branch there are issue with python paths
        with chdir(self, self.depot_tools_dir):
            self.run('gclient')

            self.run(f'git checkout {self.depot_tools_release}')

            os.environ['DEPOT_TOOLS_UPDATE'] = '0'

            self.run('gclient')


    def _create_gclient_configuration(self):
        gclientFileContent = """\
solutions = [
  {{
    "name"        : '{}',
    "url"         : 'https://github.com/webrtc-sdk/webrtc.git@{}_release',
    "deps_file"   : 'DEPS',
    "managed"     : False,
    "custom_deps" : {{}},
    "custom_vars": {{}},
  }},
]
""".format(self.webrtc_dir, self.webrtc_release)

        with open('.gclient', 'w') as file:
            file.writelines(gclientFileContent)


    def _setup_linux_dependencies(self):
        self.run('sed -i "s/} snapcraft/} /gi" build/install-build-deps.sh')
        self.run('build/install-build-deps.sh --no-prompt')

        if self.settings.arch == 'x86_64':
            self.run('python3 build/linux/sysroot_scripts/install-sysroot.py --arch=amd64')
        elif self.settings.arch == 'armv8':
            self.run('python3 build/linux/sysroot_scripts/install-sysroot.py --arch=arm64')


    def _setup_webrtc(self):
        self._create_gclient_configuration()
        
        self.run('gclient sync --jobs 16')

        with chdir(self, 'src'):
            if self.settings.os == 'Linux':
                self._setup_linux_dependencies()

            with fileinput.FileInput('BUILD.gn', inplace=True) as file:
                for line in file:
                    print(line.replace("deps = [ \":webrtc\" ]", "deps = [ \":webrtc\", \"//libwebrtc\" ]"), end='')


    def _gn_args(self):
        args = []

        if self.settings.os == 'Windows':
            args.append('target_os=\\\"win\\\"')
        elif self.settings.os == 'Linux':
            args.append('target_os=\\\"linux\\\"')

            if self.settings.arch == 'x86_64':
                args.append('target_cpu=\\\"x64\\\"')
            elif self.settings.arch == 'x86':
                args.append('target_cpu=\\\"x86\\\"')
            elif self.settings.arch == 'armv8':
                args.append('target_cpu=\\\"arm64\\\"')
        
        if self.settings.build_type == 'Debug':
            args.append('is_debug=true')
        else:
            args.append('is_debug=false')

        if self.settings.os == 'Windows':
            args.append('is_clang=true')
            args.append('libwebrtc_desktop_capture=true')
        else:
            args.append('use_custom_libcxx=false')

        if self.options.use_h264:
            args.append('rtc_use_h264=true')
            args.append('ffmpeg_branding=\\\"Chrome\\\"')
        
        args.append('is_component_build=false')
        args.append('rtc_include_tests=false')
        args.append('rtc_build_examples=false')

        return " ".join(args)
    

    def _build_webrtc(self):
        with chdir(self, 'src'):
            gn_args = self._gn_args()
            self.run(f'gn gen out --args="{gn_args}"')

            self.run("ninja -C out")

            self.run("ninja -C out libwebrtc")


    def generate(self):
        pass


    def build(self):
        self.run('ls')
        self._set_depot_tools_environment_variables()

        self._setup_depot_tools()

        self._setup_webrtc()

        self._build_webrtc()


    def package(self):
        sources_folder = os.path.join(self.build_folder, 'src', 'libwebrtc')
        copy(self, pattern="LICENSE", src=sources_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        copy(self, '*.h', src=os.path.join(sources_folder, 'include'), dst=os.path.join(self.package_folder, 'include'))
        copy(self, '*.h', src=os.path.join(sources_folder, 'include', 'base'), dst=os.path.join(self.package_folder, 'include', 'base'))

        copy(self, 'libwebrtc.dll.lib', src=os.path.join(self.build_folder, 'src', 'out'), dst=os.path.join(self.package_folder, 'lib'), keep_path=False)
        copy(self, 'libwebrtc.dll', src=os.path.join(self.build_folder, 'src', 'out'), dst=os.path.join(self.package_folder, 'lib'), keep_path=False)
        copy(self, 'libwebrtc.so', src=os.path.join(self.build_folder, 'src', 'out'), dst=os.path.join(self.package_folder, 'lib'), keep_path=False)


    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        
        self.cpp_info.libdirs = ["lib"]
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ["libwebrtc.dll"]
        else:
            self.cpp_info.libs = ["libwebrtc.so"]
