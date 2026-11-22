# Local build environment

## Installed tools

Everything was installed under the user's home directory. No sudo password was
used or saved, and the existing OpenOrbis installation was not changed.

- OrbisDev: `~/.local/opt/orbisdev`, from the official
  [Ubuntu development release](https://github.com/orbisdev/orbisdev/releases/tag/latest).
  Bundled compiler: PS4 Clang 14.0.3; linker: GNU Binutils 2.38.
- .NET SDK: `~/.local/opt/dotnet`, version 10.0.404, runtime 10.0.15.
  The archive was checked against Microsoft's published SHA512 digest.
- `pkgTool`: rebuilt from `maxton/LibOrbisPkg`, targeting `net10.0` instead of
  unsupported `netcoreapp3.0`. The original framework-dependent files remain
  under `orbisdev/bin/pkgtools`; the new files are under `pkgtools-net10`.
  The wrapper preserves argument quoting and uses the local .NET installation.
- `gp4gen` and `orbis-elf-create`: included in the OrbisDev release.

Configuration files:

- Fish: `~/.config/fish/conf.d/orbisdev.fish`.
- Bash/POSIX: `~/.config/orbisdev/env.sh`, sourced by `~/.bashrc` and `~/.profile`.
- `ORBISDEV` and `DOTNET_ROOT` are exported. Their executable directories are
  appended to PATH, leaving the system compiler first. `itemzflow/Makefile`
  selects the SDK compiler explicitly.

For an existing Fish terminal:

```fish
source ~/.config/fish/conf.d/orbisdev.fish
```

For an existing Bash/POSIX terminal:

```sh
. "$HOME/.config/orbisdev/env.sh"
```

## Dependencies built for PS4

Source checkouts are in `~/.local/share/orbisdev-sources`.

- `orbisGl`: `orbisdev/orbisdev-orbisGl`, commit
  `fbed4dd6ef35f59cdcc67efac74aec6ec90d0d53`.
- Font engine: `LightningMods/PS4-Store`, commit
  `4d08c6e6a3d54d6f35a38a830f4ec8b045ed6c43`, using the mandatory font, atlas,
  vector, matrix, and VBO APIs required by Itemzflow. Optional Store-specific
  font-manager/text-buffer code is not included.
- Supporting font headers: `orbisdev/liborbis`, commit
  `d0b11bdbd1a5ddab02cf534d145208561407847e`.
- FreeType public headers: upstream `VER-2-5-1`, commit
  `3aee429ba605e585060532c5b6d994b0ed16e4ab`. The initial OpenOrbis header copy
  lacked function declarations; it was replaced by the matching upstream version.
  The SDK's native `SceFreeTypeOl` module still supplies the implementation.
- TagLib and dumper: this repository's `external/taglib` and `external/libdumper`.
- libpng: stable `v1.6.59`, commit `cd952f49f95bb27154ae77dbb103032d95f6e580`.
- zlib: stable `v1.4`, commit `99623ef7097352da7993ba614161fd6a311e046e`.
  The original SDK archive is preserved in
  `~/.local/opt/orbisdev/share/release-backups/libz-orbisdev-release.a`.
  PS4 `z_stream` size (112 bytes) and selected offsets matched before replacement;
  this is not a claim of full runtime ABI verification.
- Packaging tool: `maxton/LibOrbisPkg`, commit
  `643477263b2644e0803e0f58b8726ea4e3f3b7d4`, with only the two core project
  target-framework values changed to `net10.0`.

Local font and PNG/zlib build recipes are saved as
`freetype-gl-orbisdev.mk` and `png-zlib-orbisdev.mk` in the source checkout directory.
Source checkouts and licenses are retained. No upstream reset/clean scripts were run.

`build-extra.sh` was inspected, not run wholesale: it rebuilds raylib and package
tools, does not install this font engine, and references .NET 3.0 outputs. The
needed tools were reused or rebuilt individually instead.

## SDK compatibility fixes

Two SDK header defects were **proven** using compile tests, not inferred:

1. `usr/include/orbis/libSceLibcInternal.h` lacked an include guard. Including
   `ps4sdk.h` and `orbisdev.h` together failed with
   `error: redefinition of 'OrbisMallocManagedSize'`. Adding `#pragma once`
   made the same test pass. Removing the guard made it fail again; the fix was restored.
2. `usr/include/user_mem.h` used `std::size_t`, `std::bad_alloc`, and
   `std::nothrow_t` before declaring them, and used obsolete allocation exception
   specifications. The SDK header now includes its required standard headers
   and keeps the old exception specification only before C++17. The test failed
   before the fix, passed with it, failed after its removal, and passed after restoration.

The tests are `sdk-header-test.c` and `sdk-memory-header-test.cpp` under the local
source checkout directory. Allocator function names and argument types were not changed.

## Verification and limits

- All installed static libraries were compiled for PS4, not for the Linux host.
- Modified UI source files compiled with PS4 Clang 14.0.3 and `-Werror`.
- Geometry and drawing-helper host tests passed. The drawing helpers also passed
  an SDK syntax check using the actual Clang vector types.
- `pkgTool` starts in both Fish and Bash. .NET 10 smoke tests passed UTF-8 SFO
  roundtripping, XTS roundtripping, synthetic PKG creation/validation, and payload reading.
- The packaging-tool dependency scan found no resolved NuGet packages. This is
  not a CVE audit of its source. Upstream obsolete-API/analyzer warnings remain.
- No console installation, screenshots, GPU timing, or memory comparison has been performed.

## Remaining blockers

The current full build stops in `itemzflow/source/sig_handler.cpp:237` and `:241`:

```text
error: no member named 'sb_copy' in 'Dumper_Options'
```

The caller asks for sandbox-copy behavior that the bundled dumper API does not
provide. A fake field would hide the mismatch without implementing that behavior;
the feature was not silently removed. A matching dumper API or an explicitly
approved caller change is still required.

The Makefile also names these absent OrbisDev link artifacts:

- `liborbis.a`
- `libSceShellCoreUtil_stub.so`
- `libSceLncUtil_stub.so`
- `libSceSaveData_stub.so`
- `libSceShellUIUtil_stub.so`

Some similarly named OpenOrbis libraries exist, but they are not drop-in stubs.
For example, their `.comment` section contains a GCC version, while OrbisDev's
converter expects a module/library/version descriptor there and reads NIDs from
the exported symbol contents. They were not renamed or copied to mask missing dependencies.

Full build logs are at `/tmp/opencode/itemzflow-build-final.log`. No new installable
Itemzflow PKG has been produced yet.
