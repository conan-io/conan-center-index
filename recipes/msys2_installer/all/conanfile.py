#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans import __version__ as conan_version
from conans.model.version import Version
import os


class MSYS2InstallerConan(ConanFile):
    name = "msys2_installer"
    version = "20210725"
    description = "MSYS2 is a software distro and building platform for Windows"
    url = "https://github.com/bincrafters/conan-msys2_installer"
    license = "MSYS license"
    exports = ["LICENSE.md"]
    build_requires = "7z_installer/1.0@conan/stable"
    short_paths = True
    options = {"exclude_files": "ANY",  # Comma separated list of file patterns to exclude from the package
               "packages": "ANY",  # Comma separated
               "additional_packages": "ANY"}    # Comma separated
    default_options = "exclude_files=*/link.exe", \
                      "packages=base-devel,binutils,gcc", \
                      "additional_packages=None"

    if conan_version < Version("0.99"):
        settings = {
            "os": ["Windows"], "arch": ["x86", "x86_64"]
        }
    else:
        settings = {
            "os_build": ["Windows"], "arch_build": ["x86", "x86_64"]
        }

    @property
    def os(self):
        return self.settings.get_safe("os_build") or self.settings.get_safe("os")

    @property
    def arch(self):
        return self.settings.get_safe("arch_build") or self.settings.get_safe("arch")

    def source(self):
        # build tools have to download files in build method when the
        # source files downloaded will be different based on architecture or OS
        pass
        
    def build(self):
        msys_arch = "x86_64" if self.arch == "x86_64" else "i686"
        archive_name = "msys2-base-{0}-{1}.tar.xz".format(msys_arch, self.version)
        url = "http://repo.msys2.org/distrib/{0}/{1}".format(msys_arch, archive_name)
        self.output.info("Download {0} into {1}".format(url, archive_name))
        tools.download(url, archive_name)
        tar_name = archive_name.replace(".xz", "")
        self.run("7z x {0}".format(archive_name))
        self.run("7z x {0}".format(tar_name))
        os.unlink(archive_name)
        os.unlink(tar_name)

        msys_dir = "msys64" if self.arch == "x86_64" else "msys32"

        packages = []
        if self.options.packages:
            packages.extend(str(self.options.packages).split(","))
        if self.options.additional_packages:
            packages.extend(str(self.options.additional_packages).split(","))

        with tools.chdir(os.path.join(msys_dir, "usr", "bin")):
            self.run('bash -l -c "pacman -Syy --noconfirm"')
            for package in packages:
                self.run('bash -l -c "pacman -S %s --noconfirm"' % package)
        
        # create /tmp dir in order to avoid
        # bash.exe: warning: could not find /tmp, please create!
        tmp_dir = os.path.join(msys_dir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        tmp_name = os.path.join(tmp_dir, 'dummy')
        with open(tmp_name, 'a'):
            os.utime(tmp_name, None)

    def package(self):
        msys_dir = "msys64" if self.arch == "x86_64" else "msys32"
        excludes = None
        if self.options.exclude_files:
            excludes = tuple(str(self.options.exclude_files).split(","))
        self.copy("*", dst=".", src=msys_dir, excludes=excludes)

    def package_info(self):
        msys_root = self.package_folder
        msys_bin = os.path.join(msys_root, "usr", "bin")
        
        self.output.info("Creating MSYS_ROOT env var : %s" % msys_root)
        self.env_info.MSYS_ROOT = msys_root
        
        self.output.info("Creating MSYS_BIN env var : %s" % msys_bin)
        self.env_info.MSYS_BIN = msys_bin

        self.output.info("Appending PATH env var with : " + msys_bin)
        self.env_info.path.append(msys_bin)
