import os
import re
import json
import textwrap

namespace_dict = {
    'gRPC': 'grpc',
    'ZLIB': 'zlib',
    'OpenSSL': 'openssl',
    'CURL': 'curl',
    'Crc32c': 'crc32c',
    'OpenSSL': 'openssl',
    'absl': 'abseil',
    'curl': 'libcurl'
}

cmp_dict = {
    'ZLIB': 'zlib',
    'SSL': 'ssl',
    'Crypto': 'crypto',
}

def translate_requires(require):
    if require == 'Threads::Threads':
        return
    
    namespace, cmp = require.split('::')
    if namespace in ['ZLIB']:
        return

    namespace = namespace_dict.get(namespace, namespace)
    cmp = cmp_dict.get(cmp, cmp)
    if namespace == 'google-cloud-cpp':
        return cmp
    elif namespace == 'abseil':
        return f'{namespace}::absl_{cmp}'
    else:
        return f'{namespace}::{cmp}'


def libname(rawname):
    if rawname.startswith('lib'):
        rawname = rawname[len('lib'):]
    rawname, _ = rawname.rsplit('.', 1)
    return rawname


def parse_targets(filename, filename_config):
    # Get targets and requirements
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    targets = {}
    target = None
    for line in lines:
        name = re.match(r'add_library\(google-cloud-cpp::([^\s]+) STATIC IMPORTED\)', line)
        if name:
            if target:
                targets[target['name']] = target.copy()
            target = {'name': name[1]}
            print(f'target: {name[1]}')
        else:
            m = re.match(r'\s+INTERFACE_LINK_LIBRARIES\s+"(.*)"', line)
            if m:
                requires = [translate_requires(r) for r in m[1].split(';')]
                requires = [r for r in requires if r]
                target['requires'] = requires
    targets[target['name']] = target.copy()

    # Get the libraries
    with open(filename_config, 'r') as f:
        lines = f.readlines()

    target = None
    for line in lines:
        t = re.match(r'set_target_properties\(google-cloud-cpp::([\w_-]+) PROPERTIES', line)
        if t:
            target = targets[t[1]]
        else:
            m = re.match(r'\s+IMPORTED_LOCATION_RELEASE\s+"\${_IMPORT_PREFIX}/lib/(.*)"', line)
            if m:
                target['libs'] = [libname(m[1])]
    
    return targets


if __name__ == '__main__':
    print("Parse targets for google-cloud-cpp")

    me = '/Users/jgsogo/.conan/data/google-cloud-cpp/1.26.1/_/_/package/24f2c49bf3055c743a09023d24734d6a9d35cd21/lib/cmake'
    targets = {}

    def parse_more_targets(folder, component):
        print(f'Work on {component}')
        filename_base = os.path.join(me, folder, f'{component}-targets')
        googleapis = parse_targets(f'{filename_base}.cmake', f'{filename_base}-release.cmake')
        targets.update(googleapis)

    parse_more_targets(folder='google_cloud_cpp_bigquery', component='google_cloud_cpp_bigquery')
    parse_more_targets(folder='google_cloud_cpp_bigtable', component='google_cloud_cpp_bigtable')
    parse_more_targets(folder='google_cloud_cpp_common', component='google_cloud_cpp_common')
    parse_more_targets(folder='google_cloud_cpp_firestore', component='firestore')
    parse_more_targets(folder='google_cloud_cpp_googleapis', component='googleapis')
    parse_more_targets(folder='google_cloud_cpp_grpc_utils', component='grpc_utils')
    parse_more_targets(folder='google_cloud_cpp_iam', component='google_cloud_cpp_iam')
    parse_more_targets(folder='google_cloud_cpp_logging', component='google_cloud_cpp_logging')
    parse_more_targets(folder='google_cloud_cpp_pubsub', component='pubsub')
    parse_more_targets(folder='google_cloud_cpp_spanner', component='spanner')
    parse_more_targets(folder='google_cloud_cpp_storage', component='storage')
    
    with open('output.json', 'w') as f:
        f.write(json.dumps(targets, indent=4))

    with open('output.py', 'w') as f:
        for name, data in targets.items():
            f.write(textwrap.dedent(f"""\
                self.cpp_info.components["{name}"].requires = [{', '.join(['"{}"'.format(it) for it in data['requires']])}]
                self.cpp_info.components["{name}"].libs = [{', '.join(['"{}"'.format(it) for it in data['libs']])}]
                
                """))
