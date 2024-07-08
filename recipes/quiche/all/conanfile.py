from conan import ConanFile
from conan.tools.files import files, get, copy
from conan.tools.scm import Git
from conan.errors import ConanException

import shlex
import os, sys
import subprocess
import glob

required_conan_version = ">=1.57.0"

def command_exists(command, cmd="which"):
    return subprocess.call([cmd, command]) == 0


class QuciheConan(ConanFile):
    name = "quiche"
    description = "🥧 Savoury implementation of the QUIC transport protocol and HTTP/3"
    url = "https://github.com/cloudflare/quiche"
    version = "0.22.0"

    license = "BSD-2-Clause"
    author = "Cloudflare, Inc"
    topics = ("cloudflare", "quiche", "rust", "quic", "http3")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], 'FFI': [True, False]}
    default_options = {"shared": False, "fPIC": True, 'FFI': True}

    package_type = "library"

    def source(self):
        get (self, **self.conan_data["sources"][self.version], strip_root=False)

        if os.path.exists('src'):
            files.shutil.rmtree ('src')

        quichesrc = glob.glob ('quiche-*')[0]

        files.rename (self, quichesrc, 'src')

        boringssl = os.path.join ('src', 'quiche', 'deps', 'boringssl')

        if len(os.listdir(boringssl)) == 0:
            # boringssl is empty! Lets fix that!
            git = Git(self)
            git.clone ('https://github.com/google/boringssl.git', boringssl)

    def generate(self):
        cmd = "which"
        if self.settings.os == "Windows":
            cmd = "where"
        
        if not command_exists('cargo', cmd):
            raise ConanException ("This project made on rust, so the OS must provide the 'cargo'. Can not find the 'cargo' (which cargo)")

    def build(self):
        args = ['cargo', 'build', '--manifest-path', os.path.join('src', 'Cargo.toml'), '--lib', '--release']

        if self.options['FFI']:
            args.append ('--features')
            args.append ('ffi')

        result = subprocess.call (args)

        if result != 0:
            raise ConanException ("Cargo sent an invalid code. can not compile a src")

    def package_id(self):
        self.info.clear()
        
    def package(self):
        release = os.path.join ('src', 'target', 'release')

        libpkg = os.path.join (self.package_folder, 'lib')
        includepkg = os.path.join (self.package_folder, 'include')

        if not os.path.exists(libpkg):
            os.mkdir (libpkg)

        if not os.path.exists(includepkg):
            os.mkdir (includepkg)

        include = os.path.join ('src', 'quiche', 'include')

        # lib*
        for item in glob.glob (os.path.join (release, 'lib*')):
            if len(item) > 3 and item[-3:] == '.so':
                # workaround
                files.shutil.copy (item, os.path.join (libpkg, os.path.basename(item) + '.0'))
            
            files.shutil.copy (item, libpkg)

        for item in glob.glob (os.path.join (release, '*.dll')):
            files.shutil.copy (item, libpkg)

        files.shutil.copy (os.path.join(include, 'quiche.h'), includepkg)

        # License
        copy (self, 'COPYING', src=os.path.join(self.source_folder, 'src'), dst=os.path.join(self.package_folder, 'licenses', 'quiche'))
        copy (self, 'LICENSE', src=os.path.join(self.source_folder, 'src', 'quiche', 'deps', 'boringssl'), dst=os.path.join(self.package_folder, 'licenses', 'boringssl'))
    def package_info(self):
        self.cpp_info.set_property ("cmake_find_mode", "both")
        self.cpp_info.set_property ("cmake_file_name", "quiche")
        self.cpp_info.set_property ("cmake_target_name", "quiche::quiche")
        self.cpp_info.set_property ("pkg_config_name", "quiche")
        self.cpp_info.libs = ["quiche"]

