#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.tools import (
    llvm_objdump_path,
)
from extract_utils.utils import (
    run_cmd,
)

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'libspeakercalibration',
        'audio.primary.lahaina',
    ): lib_fixup_vendor_suffix,
}

namespace_imports = [
    'vendor/samsung/sm8350-common',
    'vendor/qcom/opensource/display',
    'hardware/qcom-caf/wlan',
    'device/samsung/sm8350-common',
    'hardware/qcom-caf/sm8350',
]

def blob_fixup_nop_call(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    call_instruction: str,
    disassemble_symbol: str,
    symbol: str,
    *args,
    **kwargs,
):
    for line in run_cmd(
        [
            llvm_objdump_path,
            f'--disassemble-symbols={disassemble_symbol}',
            file_path,
        ]
    ).splitlines():
        line = line.split(maxsplit=3)

        if len(line) != 4:
            continue

        offset, _, instruction, args = line

        if instruction != call_instruction:
            continue

        if not args.endswith(f' <{symbol}>'):
            continue

        with open(file_path, 'rb+') as f:
            f.seek(int(offset[:-1], 16))
            f.write(b'\x1f\x20\x03\xd5')  # AArch64 NOP

        break

blob_fixups: blob_fixups_user_type = {
    ('vendor/lib64/unihal_android.so', 'vendor/lib/unihal_android.so'): blob_fixup()
        .add_needed('libui_shim.so'),
    'vendor/lib64/vendor.qti.hardware.camera.postproc@1.0-service-impl.so': blob_fixup()
        .call(blob_fixup_nop_call, 'bl', '__cfi_check', '_ZN7android8hardware22configureRpcThreadpoolEmb@plt'),
    'vendor/lib64/nfc_nci_nxpsn.so': blob_fixup()
        .add_needed('libbase_shim.so'),
    ('vendor/lib/libmmcamera_faceproc.so') : blob_fixup()
        .clear_symbol_version('__gnu_Unwind_Find_exidx')
        .clear_symbol_version('__aeabi_memset')
        .clear_symbol_version('__aeabi_memcpy'),
    ('vendor/lib64/J12QS_libTsAe.so', 'vendor/lib64/J10QS_libTsAeFront.so', 'vendor/lib64/libTsAf_B2Q.so'): blob_fixup()
        .fix_soname(),
}  # fmt: skip

module = ExtractUtilsModule(
    'b2q',
    'samsung',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8350-common', module.vendor
    )
    utils.run()
