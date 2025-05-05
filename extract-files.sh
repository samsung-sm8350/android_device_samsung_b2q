#!/bin/bash
#
# Copyright (C) 2023 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

function blob_fixup() {
    case "${1}" in
        vendor/lib/vendor.qti.hardware.camera.postproc@1.0-service-impl.so)
            sed -i 's/configureRpcThreadpool/configureRpcTh_pathced/g' "${2}"
            "${PATCHELF}" --add-needed "libhidlbase_shim_sm8350.so" "${2}"
            #xxd -p -c0 "${2}" | sed "s/1d491e4a062079447a4408e004200121/1d491e4a062079447a4408e005200121/g" | xxd -r -p > "${2}".patched
            #mv "${2}".patched "${2}"
            ;;
        vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so)
            sed -i 's/configureRpcThreadpool/configureRpcTh_pathced/g' "${2}"
            "${PATCHELF}" --add-needed "libhidlbase_shim_sm8350.so" "${2}"
            #xxd -p -c0 "${2}" | sed "s/42b03091c00080520900001480008052/42b03091c000805209000014a0008052/g" | xxd -r -p > "${2}".patched
            #mv "${2}".patched "${2}"
            ;;
    esac
}

# If we're being sourced by the common script that we called,
# stop right here. No need to go down the rabbit hole.
if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
    return
fi

set -e

export DEVICE=b2q
export DEVICE_COMMON=sm8350-common
export VENDOR=samsung

"./../../${VENDOR}/${DEVICE_COMMON}/extract-files.sh" "$@"
