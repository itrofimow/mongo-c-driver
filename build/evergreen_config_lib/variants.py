# Copyright 2018-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from evergreen_config_lib import ConfigObject, OD


class Variant(ConfigObject):
    def __init__(self, name, display_name, run_on, tasks, expansions=None,
                 batchtime=None):
        super(Variant, self).__init__()
        self._variant_name = name
        self.display_name = display_name
        self.run_on = run_on
        self.tasks = tasks
        self.expansions = expansions
        self.batchtime = batchtime

    @property
    def name(self):
        return self._variant_name

    def to_dict(self):
        v = super(Variant, self).to_dict()
        for i in 'display_name', 'expansions', 'run_on', 'tasks', 'batchtime':
            if getattr(self, i):
                v[i] = getattr(self, i)
        return v


mobile_flags = (
    ' -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY'
    ' -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY'
    ' -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER'
    ' -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY'
)


def ios(sdk):
    arch = 'arm64' if sdk == 'iphoneos' else 'x86_64'
    root = '$(xcrun --sdk %s --show-sdk-path)' % (sdk,)
    cflags = '-arch %s -isysroot %s -miphoneos-version-min=10.2' % (arch, root)
    flags = mobile_flags + (
        ' -DCMAKE_SYSTEM_NAME=Darwin'
        ' -DCMAKE_FIND_ROOT_PATH="%s"'
        ' -DCMAKE_INSTALL_NAME_DIR=@rpath'
        ' -DCMAKE_C_FLAGS="%s"'
    ) % (root, cflags)

    env = 'DEVELOPER_DIR=/Applications/Xcode9.2.app'

    return OD([('libmongocapi_cmake_flags', flags),
               ('libmongocapi_compile_env', env)])


def android(abi):
    toolchain = './android_sdk/ndk-bundle/build/cmake/android.toolchain.cmake'
    flags = mobile_flags + (
        ' -DANDROID_NATIVE_API_LEVEL=21'
        ' -DANDROID_ABI=%s'
        ' -DTHREADS_PTHREAD_ARG=2'
        ' -DCMAKE_TOOLCHAIN_FILE=%s'
        ' -DCMAKE_FIND_ROOT_PATH="./android_toolchain"'
        ' -DCMAKE_INSTALL_RPATH=\\$ORIGIN/../lib'
    ) % (abi, toolchain)

    toolchain_arch = 'arm64' if abi == 'arm64-v8a' else abi
    setup = ('JAVA_HOME=/opt/java/jdk8/'
             ' ./.evergreen/setup-android-toolchain.sh %s %s'
             ) % (abi, toolchain_arch)

    return OD([('libmongocapi_cmake_flags', flags),
               ('setup_android_toolchain', setup)])


all_variants = [
    Variant('releng',
            '**Release Archive Creator',
            'ubuntu1604-test',
            ['make-release-archive',
             'release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile .stdflags',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             'debug-compile-valgrind',
             'debug-compile-no-counters',
             'compile-tracing',
             'debian-package-build',
             OD([('name', 'rpm-package-build'),
                 ('distros', ['rhel70'])]),
             'link-with-cmake',
             'abi-compliance-check',
             'link-with-cmake-ssl',
             'link-with-cmake-snappy',
             OD([('name', 'link-with-cmake-mac'), ('distros', ['macos-1012'])]),
             OD([('name', 'link-with-cmake-windows'),
                 ('distros', ['windows-64-vs2015-compile'])]),
             OD([('name', 'link-with-cmake-windows-ssl'),
                 ('distros', ['windows-64-vs2015-compile'])]),
             OD([('name', 'link-with-cmake-windows-snappy'),
                 ('distros', ['windows-64-vs2015-compile'])]),
             OD([('name', 'link-with-cmake-mingw'),
                 ('distros', ['windows-64-vs2013-compile'])]),
             OD([('name', 'link-with-pkg-config'),
                 ('distros', ['ubuntu1604-test'])]),
             OD([('name', 'link-with-pkg-config-mac'),
                 ('distros', ['macos-1012'])]),
             'link-with-pkg-config-ssl',
             'link-with-bson',
             OD([('name', 'link-with-bson-windows'),
                 ('distros', ['windows-64-vs2015-compile'])]),
             OD([('name', 'link-with-bson-mac'), ('distros', ['macos-1012'])]),
             OD([('name', 'link-with-bson-mingw'),
                 ('distros', ['windows-64-vs2013-compile'])]),
             'check-public-headers',
             'install-uninstall-check',
             OD([('name', 'install-uninstall-check-mingw'),
                 ('distros', ['windows-64-vs2015-compile'])]),
             OD([('name', 'install-uninstall-check-msvc'),
                 ('distros', ['windows-64-vs2015-compile'])])]),
    Variant('clang34ubuntu',
            'clang 3.4 (Ubuntu 14.04)',
            'ubuntu1404-build',
            ['debug-compile-scan-build',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-rdtscp',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.4.0 .openssl !.nosasl .server',
             '.3.6 .openssl !.nosasl .server',
             '.3.4 .openssl !.nosasl .server',
             '.3.2 .openssl !.nosasl .server',
             '.3.0 .openssl !.nosasl !.auth'],
            {'CC': 'clang'}),
    Variant('clang35',
            'clang 3.5 (Debian 8.1)',
            'debian81-test',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile .stdflags !.c89',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server'],
            {'CC': 'clang'}),
    Variant('openssl',
            'OpenSSL / LibreSSL',
            'archlinux-build',
            ['build-and-run-authentication-tests-openssl-0.9.8',
             'build-and-run-authentication-tests-openssl-1.0.0',
             'build-and-run-authentication-tests-openssl-1.0.1',
             'build-and-run-authentication-tests-openssl-1.0.2',
             'build-and-run-authentication-tests-openssl-1.1.0',
             'build-and-run-authentication-tests-openssl-1.0.1-fips',
             'build-and-run-authentication-tests-libressl-2.5']),
    Variant('clang37',
            'clang 3.7 (Archlinux)',
            'archlinux-test',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile .stdflags !.c89',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .nossl',
             '.4.0 .nossl',
             '.3.6 .nossl',
             '.3.4 .nossl',
             '.3.2 .nossl',
             '.3.0 .nossl .nosasl !.auth'],
            {'CC': 'clang'}),
    Variant('clang38-i386',
            'clang 3.8 (i386) (Ubuntu 16.04)',
            'ubuntu1604-test',
            ['debug-compile-scan-build',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile .stdflags !.c89',
             '.debug-compile !.sspi .nossl .nosasl',
             '.latest .nossl .nosasl',
             '.4.0 .nossl .nosasl',
             '.3.6 .nossl .nosasl'],
            {'CC': 'clang', 'MARCH': 'i386'}),
    Variant('clang38',
            'clang 3.8 (Ubuntu 16.04)',
            'ubuntu1604-test',
            ['.compression',
             'debug-compile-scan-build',
             'debug-compile-asan-clang',
             'debug-compile-ubsan',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile .stdflags !.c89',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.authentication-tests .valgrind',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server',
             '.3.6 .openssl !.nosasl .server'],
            {'CC': 'clang'}),
    Variant('gcc46',
            'GCC 4.6 (Ubuntu 12.04)',
            'ubuntu1204-test',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-rdtscp',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.3.6 .openssl !.nosasl .server',
             '.3.4 .openssl !.nosasl .server',
             '.3.2 .openssl !.nosasl .server',
             '.3.0 .openssl !.nosasl !.auth'],
            {'CC': 'gcc'}),
    Variant('gcc48ubuntu',
            'GCC 4.8 (Ubuntu 14.04)',
            'ubuntu1404-build',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.latest .nossl !.ipv4-ipv6',
             '.4.0 .openssl !.nosasl .server',
             '.3.6 .openssl !.nosasl .server',
             '.3.4 .openssl !.nosasl .server',
             '.3.2 .openssl !.nosasl .server',
             '.3.0 .openssl !.nosasl !.auth',
             '.latest .openssl .nosasl .replica_set',
             '.latest .openssl !.nosasl .replica_set'],
            {'CC': 'gcc'}),
    Variant('gcc48rhel',
            'GCC 4.8 (RHEL 7.0)',
            'rhel70',
            ['.hardened',
             '.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server',
             '.3.6 .openssl !.nosasl .server',
             '.3.4 .openssl !.nosasl .server',
             '.3.2 .openssl !.nosasl .server',
             '.3.0 .openssl !.nosasl !.auth'],
            {'CC': 'gcc'}),
    Variant('gcc49',
            'GCC 4.9 (Debian 8.1)',
            'debian81-test',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server'],
            {'CC': 'gcc'}),
    Variant('gcc54-i386',
            'GCC 5.4 (i386) (Ubuntu 16.04)',
            'ubuntu1604-test',
            ['debug-compile-coverage',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile !.sspi .nossl .nosasl',
             '.latest .nossl .nosasl',
             '.4.0 .nossl .nosasl'],
            {'CC': 'gcc', 'MARCH': 'i386'}),
    Variant('gcc54',
            'GCC 5.4 (Ubuntu 16.04)',
            'ubuntu1604-test',
            ['.compression',
             'debug-compile-asan-gcc',
             'debug-compile-coverage',
             'debug-compile-nosrv',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.authentication-tests .valgrind',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             'retry-true-3.4-replica-set',
             'retry-true-latest-server',
             '.4.0 .openssl !.nosasl .server',
             'test-dns-openssl',
             'test-dns-auth-openssl'],
            {'CC': 'gcc'}),
    Variant('darwin',
            '*Darwin, macOS (Apple LLVM)',
            'macos-1012',
            ['.compression !.snappy',
             'debug-compile-coverage',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-rdtscp',
             'debug-compile-no-align',
             'debug-compile-nosrv',
             '.debug-compile .darwinssl',
             '.debug-compile !.sspi .nossl',
             '.debug-compile .clang',
             '.authentication-tests .darwinssl',
             '.latest .darwinssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .darwinssl !.nosasl .server',
             '.3.6 .darwinssl !.nosasl .server',
             '.3.4 .darwinssl !.nosasl .server',
             '.3.2 .darwinssl !.nosasl .server',
             '.3.2 .nossl',
             'test-dns-darwinssl',
             'test-dns-auth-darwinssl',
             'debug-compile-lto',
             'debug-compile-lto-thin'],
            {'CC': 'clang'}),
    Variant('windows-2015',
            'Windows (VS 2015)',
            'windows-64-vs2015-compile',
            ['.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             'debug-compile-nosrv',
             '.debug-compile .winssl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.debug-compile .sspi',
             '.authentication-tests .openssl !.sasl',
             '.authentication-tests .winssl',
             '.latest .winssl !.nosasl .server',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .winssl !.nosasl .server',
             '.3.6 .winssl !.nosasl .server',
             '.3.4 .winssl !.nosasl .server',
             '.3.2 .winssl !.nosasl .server',
             '.3.0 .nossl',
             'test-dns-winssl',
             'test-dns-auth-winssl'],
            {'CC': 'Visual Studio 14 2015 Win64'}),
    Variant('windows-2015-32',
            'Windows (i386) (VS 2015)',
            'windows-64-vs2015-compile',
            ['.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile .sspi !.openssl',
             '.debug-compile .winssl .nosasl',
             '.debug-compile !.sspi .nossl .nosasl',
             '.authentication-tests .winssl',
             '.latest .winssl .nosasl .server',
             '.latest .nossl .nosasl',
             '.latest .sspi',
             '.4.0 .winssl .nosasl .server'],
            {'CC': 'Visual Studio 14 2015'}),
    Variant('windows-2013',
            'Windows (VS 2013)',
            'windows-64-vs2013-compile',
            ['.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile .winssl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.debug-compile .sspi',
             '.authentication-tests .openssl !.sasl',
             '.authentication-tests .winssl',
             '.latest .winssl !.nosasl .server',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.latest .sspi',
             '.4.0 .winssl !.nosasl .server'],
            {'CC': 'Visual Studio 12 2013 Win64'}),
    Variant('windows-2013-32',
            'Windows (i386) (VS 2013)',
            'windows-64-vs2013-compile',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-rdtscp',
             '.debug-compile .sspi !.openssl',
             '.debug-compile .winssl .nosasl',
             '.debug-compile !.sspi .nossl .nosasl',
             '.authentication-tests .winssl',
             '.latest .winssl .nosasl .server',
             '.latest .nossl .nosasl',
             '.latest .sspi',
             '.4.0 .winssl .nosasl .server'],
            {'CC': 'Visual Studio 12 2013'}),
    Variant('windows-2010',
            'Windows (VS 2010)',
            'windows-64-vs2010-compile',
            ['.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-rdtscp',
             '.debug-compile .winssl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.debug-compile .sspi',
             '.authentication-tests .openssl !.sasl',
             '.authentication-tests .winssl',
             '.latest .winssl !.nosasl .server',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.latest .sspi',
             '.4.0 .winssl !.nosasl .server'],
            {'CC': 'Visual Studio 10 2010 Win64'}),
    Variant('windows-2010-32',
            'Windows (i386) (VS 2010)',
            'windows-64-vs2010-compile',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile .winssl .sspi',
             '.debug-compile .winssl .nosasl',
             '.debug-compile !.sspi .nossl .nosasl',
             '.debug-compile .nossl .sspi',
             '.authentication-tests .winssl',
             '.latest .winssl .nosasl .server',
             '.latest .nossl .nosasl',
             '.latest .sspi',
             '.4.0 .winssl .nosasl .server'],
            {'CC': 'Visual Studio 10 2010'}),
    Variant('mingw',
            'MinGW-W64',
            'windows-64-vs2013-compile',
            ['debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile .nossl .nosasl',
             '.debug-compile .winssl .sspi',
             '.latest .nossl .nosasl .server',
             '.latest .winssl .sspi .server'],
            {'CC': 'mingw'}),
    Variant('power8-rhel71',
            '*Power8 (ppc64le) (RHEL 7.1)',
            'rhel71-power8-build',
            ['.compression !.snappy',
             'release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl !.sasl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server'],
            {'CC': 'gcc'},
            batchtime=1440),
    Variant('power8-ubuntu1604',
            'Power8 (ppc64le) (Ubuntu 16.04)',
            'ubuntu1604-power8-test',
            ['debug-compile-scan-build',
             'debug-compile-coverage',
             'release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server',
             'test-dns-openssl'],
            {'CC': 'gcc'},
            batchtime=1440),
    Variant('arm-ubuntu1604',
            '*ARM (aarch64) (Ubuntu 16.04)',
            'ubuntu1604-arm64-large',
            ['.compression !.snappy',
             'debug-compile-scan-build',
             'debug-compile-coverage',
             'debug-compile-no-align',
             'release-compile',
             'debug-compile-nosasl-nossl',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server',
             'test-dns-openssl'],
            {'CC': 'gcc'},
            batchtime=1440),
    Variant('zseries-rhel72',
            '*zSeries',
            'rhel72-zseries-test',
            ['release-compile',
             'debug-compile-nosasl-nossl',
             'debug-compile-no-align',
             '.debug-compile !.sspi .openssl',
             '.debug-compile !.sspi .nossl',
             '.authentication-tests .openssl',
             '.latest .openssl !.nosasl .server',
             '.latest .nossl',
             '.4.0 .openssl !.nosasl .server'],
            {'CC': 'gcc'},
            batchtime=1440),
    Variant('valgrind-ubuntu',
            'Valgrind Tests (Ubuntu 14.04)',
            'ubuntu1404-build',
            ['.debug-compile !.sspi .openssl !.sasl',
             '.debug-compile !.sspi .nossl !.sasl',
             '.debug-compile .special .valgrind',
             '.test-valgrind'],
            {'CC': 'gcc'},
            batchtime=10080),
    Variant('asan-ubuntu',
            'ASAN Tests (Ubuntu 14.04)',
            'ubuntu1404-test',
            ['.debug-compile .asan-clang',
             '.test-asan'],
            {'CC': 'clang'},
            batchtime=1440),
    Variant('code-coverage-ubuntu',
            'Code Coverage Tests',
            'ubuntu1404-build',
            ['.test-coverage'],
            {'CC': 'gcc'},
            batchtime=1440),
    Variant('ios-102-debug',
            'iOS 10.2 DEBUG',
            'macos-1012',
            ['compile-libmongocapi'],
            ios('iphoneos'),
            batchtime=1440),
    Variant('ios-sim-102-debug',
            'iOS Simulator 10.2 DEBUG',
            'macos-1012',
            ['compile-libmongocapi'],
            ios('iphonesimulator'),
            batchtime=1440),
    Variant('android-debug-arm64',
            'Android arm64 (Ubuntu 16.04)',
            'ubuntu1604-build',
            ['compile-libmongocapi'],
            android('arm64-v8a'),
            batchtime=1440),
    Variant('android-debug-x86',
            'Android x86_64 (Ubuntu 16.04)',
            'ubuntu1604-build',
            ['compile-libmongocapi'],
            android('x86_64'),
            batchtime=1440),
]
