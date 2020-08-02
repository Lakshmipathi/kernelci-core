#!/bin/bash
set -ue

# Important: This script is run under QEMU

# Build-depends needed to build the test suites, they'll be removed later
BUILD_DEPS="\
    gcc \
    git \
    make \
    pkgconf \
    autoconf \
    automake \
    bison \
    flex \
    m4 \
    libc6-dev \
"

apt-get update -y
apt-get install -y ${BUILD_DEPS}

########################################################################
# Build tests                                                          #
########################################################################

BUILDFILE=/test_suites.json
echo '{  "tests_suites": [' >> $BUILDFILE

########################################################################
# Build and install tests                                              #
########################################################################
BUILD_DIR="/ltp"
mkdir -p ${BUILD_DIR} && cd ${BUILD_DIR}

git config --global http.sslverify false
LTP_URL="https://github.com/linux-test-project/ltp.git"
LTP_SHA=$(git ls-remote ${LTP_URL} | head -n 1 | cut -f 1)

git clone --depth=1 ${LTP_URL}
cd ltp && make autotools && ./configure && make all

find . -executable -type f -exec strip {} \;
make install

echo '    {"name": "ltp-tests", "git_url": "'$LTP_URL'", "git_commit": "'$LTP_SHA'" }' >> $BUILDFILE
echo '  ]}' >> $BUILDFILE

########################################################################
# Cleanup: remove files and packages we don't want in the images       #
########################################################################

rm -rf ${BUILD_DIR}
apt-get remove --purge -y ${BUILD_DEPS} perl-modules-5.28
apt-get autoremove --purge -y
apt-get clean

