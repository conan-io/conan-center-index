from conans import ConanFile, tools, util
from conans.errors import ConanException
import os
import tempfile
import subprocess
import json
import re
import shutil
from conans import __version__ as conan_version
from conans.tools import Version


def _get_file_attrs(glob, recursive=False):
    try:
        cmd = ["attrib"]
        if recursive:
            cmd.extend(["/D", "/S"])
        cmd.append(glob)
        output = subprocess.check_output(cmd)
        lines = util.files.decode_text(output).split("\r\n")
    except (ValueError, IOError, subprocess.CalledProcessError, UnicodeDecodeError) as e:
        raise ConanException("attrib run error: %s" % str(e))
    attrib_re = re.compile(r'^([RASHOIXVPU ]+ )(([A-Z]:|\\)\\.*)')
    files = []
    for line in lines:
        match_obj = attrib_re.match(line)
        if match_obj:
            attrs = match_obj.group(1).replace(' ', '')
            path = match_obj.group(2)
            files.append((path, attrs))
    return files


class CygwinInstallerConan(ConanFile):
    name = "cygwin"
    description = "Cygwin is a distribution of popular GNU and other Open Source tools running on Windows"
    topics = ("conan", "cygwin", "tools")
    license = "https://cygwin.com/COPYING"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cygwin.com"
    settings = {"os_build": ["Windows"], "arch_build": ["x86", "x86_64"]}
    install_dir = 'cygwin-install'
    short_paths = True
    options = {"packages": "ANY",  # Comma separated, https://cygwin.com/packages/package_list.html
               "additional_packages": "ANY",  # Comma separated, https://cygwin.com/packages/package_list.html
               "exclude_files": "ANY",  # Comma separated list of file patterns to exclude from the package
               "no_acl": [True, False],
               "cygwin": "ANY",  # https://cygwin.com/cygwin-ug-net/using-cygwinenv.html
               "db_enum": "ANY",  # https://cygwin.com/cygwin-ug-net/ntsec.html#ntsec-mapping-nsswitch
               "db_home": "ANY",
               "db_shell": "ANY",
               "db_gecos": "ANY",
               "with_sage": [True, False]}  # sage package manager https://github.com/svnpenn/sage
    default_options = {
        'packages': 'pkg-config,make,libtool,binutils,gcc-core,gcc-g++,autoconf,automake,gettext,curl',
        'additional_packages': 'None',
        'exclude_files': 'None',
        'no_acl': False,
        'cygwin': 'None',
        'db_enum': 'None',
        'db_home': 'None',
        'db_shell': 'None',
        'db_gecos': 'None',
        'with_sage': True
    }

    @property
    def os(self):
        return self.settings.get_safe("os_build") or self.settings.get_safe("os")

    @property
    def arch(self):
        return self.settings.get_safe("arch_build") or self.settings.get_safe("arch")

    def build(self):
        filename = "setup-%s.exe" % self.arch
        url = "https://cygwin.com/%s" % filename
        tools.download(url, filename)

        if not os.path.isdir(self.install_dir):
            os.makedirs(self.install_dir)

        # https://cygwin.com/faq/faq.html#faq.setup.cli
        command = filename
        command += ' --arch %s' % self.arch
        # Disable creation of desktop and start menu shortcuts
        command += ' --no-shortcuts'
        # Do not check for and enforce running as Administrator
        command += ' --no-admin'
        # Unattended setup mode
        command += ' --quiet-mode'
        command += ' --root %s' % os.path.abspath(self.install_dir)
        # TODO : download and parse mirror list, probably also select the best one
        command += ' -s http://cygwin.mirror.constant.com'
        command += ' --local-package-dir %s' % tempfile.mkdtemp()
        packages = []
        if self.options.packages:
            packages.extend(str(self.options.packages).split(","))
        if self.options.additional_packages:
            packages.extend(str(self.options.additional_packages).split(","))
        if packages:
            command += ' --packages %s' % ','.join(packages)
        self.run(command)

        os.unlink(filename)

        # create /tmp dir in order to avoid
        # bash.exe: warning: could not find /tmp, please create!
        tmp_dir = os.path.join(self.install_dir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        tmp_name = os.path.join(tmp_dir, 'dummy')
        with open(tmp_name, 'a'):
            os.utime(tmp_name, None)

        def add_line(line):
            nsswitch_conf = os.path.join(self.install_dir, 'etc', 'nsswitch.conf')
            with open(nsswitch_conf, 'a') as f:
                f.write('%s\n' % line)

        if self.options.db_enum:
            add_line('db_enum: %s' % self.options.db_enum)
        if self.options.db_home:
            add_line('db_home: %s' % self.options.db_home)
        if self.options.db_shell:
            add_line('db_shell: %s' % self.options.db_shell)
        if self.options.db_gecos:
            add_line('db_gecos: %s' % self.options.db_gecos)

        if self.options.no_acl:
            fstab = os.path.join(self.install_dir, 'etc', 'fstab')
            fstab_in = fstab + ".in"
            shutil.copyfile(fstab, fstab_in)
            tools.replace_in_file(fstab_in,
"""# This is default anyway:
none /cygdrive cygdrive binary,posix=0,user 0 0""",
"""none /cygdrive cygdrive noacl,binary,posix=0,user 0 0
@CYGWIN_ROOT@/bin /usr/bin ntfs binary,auto,noacl           0 0
@CYGWIN_ROOT@/lib /usr/lib ntfs binary,auto,noacl           0 0
@CYGWIN_ROOT@     /        ntfs override,binary,auto,noacl  0 0""")

        if self.options.with_sage:
            usr_local = os.path.join(self.install_dir, 'usr', 'local')
            bash = os.path.abspath(os.path.join(self.install_dir, 'bin', 'bash.exe'))
            with tools.chdir(usr_local):
                for package in ['velour', 'sage']:
                    tools.get('https://codeload.github.com/svnpenn/%s/zip/master' % package)
                    self.run('%s -l -c "cd /usr/local/%s-master && ./install.sh"' % (bash, package))

    def record_symlinks(self):
        root = os.path.join(self.build_folder, self.install_dir)
        symlinks = [os.path.relpath(path, root)
                    for (path, attrs) in _get_file_attrs(os.path.join(root, '*'), recursive=True)
                    if "S" in attrs]
        symlinks_json = os.path.join(self.package_folder, "symlinks.json")
        tools.save(symlinks_json, json.dumps(symlinks))

    def package(self):
        self.record_symlinks()
        excludes = None
        if self.options.exclude_files:
            excludes = tuple(str(self.options.exclude_files).split(","))
        self.copy(pattern="*", dst=".", src=self.install_dir, excludes=excludes)

    def fix_symlinks(self):
        symlinks_json = os.path.join(self.package_folder, "symlinks.json")
        symlinks = json.loads(tools.load(symlinks_json))
        for path in symlinks:
            full_path = os.path.join(self.package_folder, path)
            attrs = _get_file_attrs(full_path)[0][1]
            if 'S' in attrs:
                break
            self.run('attrib -R +S "%s"' % full_path)

    def package_id(self):
        del self.info.options.cygwin

    def package_info(self):
        # workaround for error "cannot execute binary file: Exec format error"
        # symbolic links must have system attribute in order to work properly
        self.fix_symlinks()

        cygwin_root = self.package_folder
        cygwin_root_fs = cygwin_root.replace('\\', '/')
        cygwin_bin = os.path.join(cygwin_root, "bin")

        if self.options.no_acl:
            fstab = os.path.join(cygwin_root, 'etc', 'fstab')
            self.output.info("Updating /etc/fstab")
            shutil.copyfile(fstab + ".in", fstab)
            tools.replace_in_file(fstab, "@CYGWIN_ROOT@", cygwin_root_fs)

        self.output.info("Creating CYGWIN_ROOT env var : %s" % cygwin_root)
        self.env_info.CYGWIN_ROOT = cygwin_root

        self.output.info("Creating CYGWIN_BIN env var : %s" % cygwin_bin)
        self.env_info.CYGWIN_BIN = cygwin_bin

        self.output.info("Appending PATH env var with : " + cygwin_bin)
        self.env_info.path.append(cygwin_bin)

        if self.options.cygwin:
            self.output.info("Creating CYGWIN env var : %s" % self.options.cygwin)
            self.env_info.CYGWIN = str(self.options.cygwin)

