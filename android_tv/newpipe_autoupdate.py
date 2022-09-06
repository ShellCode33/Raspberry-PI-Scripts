#!/usr/bin/env python3
# coding: utf-8

import requests
import shutil
from subprocess import check_output, STDOUT
from pkg_resources import parse_version
from tempfile import TemporaryDirectory

from typing import Union

API_URL = "https://api.github.com/repos/TeamNewPipe/NewPipe/releases"

def get_installed_version() -> Union[str, None]:
    stdout = check_output(["adb", "shell", "dumpsys", "package", "org.schabi.newpipe"], stderr=STDOUT)

    for line in stdout.decode().split("\n"):
        if "versionName" in line:
            return line.split("=")[1]

    return None

def get_remote_version() -> (str, str):
    resp = requests.get(f"{API_URL}/latest")
    latest_version = resp.json()["name"][1:]

    for asset in resp.json()["assets"]:
        if asset["name"].endswith(".apk"):
            apk_asset_url = asset["url"]
            break

    resp = requests.get(apk_asset_url)
    apk_download_url = resp.json()["browser_download_url"]

    return latest_version, apk_download_url

def install_apk_from_url(download_url: str) -> None:
    with TemporaryDirectory() as tmp_dir:
        local_filename = download_url.split('/')[-1]
        local_filepath = f"{tmp_dir}/{local_filename}"

        with requests.get(download_url, stream=True) as r:
            with open(local_filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        check_output(["adb", "install", local_filepath])

def main() -> None:
    current_version = get_installed_version()
    remote_version, apk_download_url = get_remote_version()

    if current_version is None or parse_version(current_version) < parse_version(remote_version):
        install_apk_from_url(apk_download_url)
        print(f"Upgraded NewPipe from {current_version} to {remote_version}")
    else:
        print(f"NewPipe is already up to date (v{current_version})")

if __name__ == "__main__":
    main()
