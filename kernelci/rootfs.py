# Copyright (C) 2019 Collabora Limited
# Author: Lakshmipathi G <lakshmipathi.ganapathi@collabora.com>
#
# This module is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from kernelci import shell_cmd
import os
import requests
from urllib.parse import urljoin


def _build_debos(name, config, data_path):
    cwd = os.getcwd()
    os.chdir(data_path)
    for arch_type in config.arch_list:
        cmd = 'debos \
-t architecture:{arch} \
-t suite:{release_name} \
-t basename:{name}/{arch} \
-t extra_packages:"{extra_packages}" \
-t extra_packages_remove:"{extra_packages_remove}" \
-t extra_files_remove:"{extra_files_remove}" \
-t script:"{script}" \
-t test_overlay:"{test_overlay}" \
-t crush_image_options:"{crush_image_options}" \
rootfs.yaml'.format(
            name=name,
            data_path=data_path,
            arch=arch_type,
            release_name=config.debian_release,
            extra_packages=" ".join(config.extra_packages),
            extra_packages_remove=" ".join(config.extra_packages_remove),
            extra_files_remove=" ".join(config.extra_files_remove),
            script=config.script,
            test_overlay=config.test_overlay,
            crush_image_options=" ".join(config.crush_image_options)
            )
        ret_code = shell_cmd(cmd, True)
        if not ret_code:
            return False

    os.chdir(cwd)
    return True


def build(name, config, data_path):
    if config.rootfs_type == "debos":
        return _build_debos(name, config, data_path)
    else:
        print("rootfs_type:{} not supported".format(config.rootfs_type))
        return False


def _upload_files(api, token, path, input_files):
    headers = {
        'Authorization': token,
    }
    data = {
        'path': path,
    }
    files = {
        'file{}'.format(i): (name, fobj)
        for i, (name, fobj) in enumerate(input_files.items())
    }
    url = urljoin(api, '/upload')
    resp = requests.post(url, headers=headers, data=data, files=files)
    print(resp.text)
    resp.raise_for_status()
    return True


def upload(api, token, storage, rootfsdir):
    """Upload rootfs to KernelCI backend.

    *api* is the URL of the KernelCI backend API
    *token* is the backend API token to use
    *storage* is the target on KernelCI backend
    *rootfsdir* is the local rootfs directory path to upload
    """
    artifacts = {}
    for root, _, files in os.walk(rootfsdir):
        for f in files:
            px = os.path.relpath(root, rootfsdir)
            artifacts[os.path.join(px, f)] = open(os.path.join(root, f), "rb")
    _upload_files(api, token, storage, artifacts)
    return True
