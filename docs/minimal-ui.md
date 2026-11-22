# Minimal UI

## Direction and references

Itemzflow is a native C++ / OpenGL ES 2 application for PS4, not a web app.
The redesign uses charcoal surfaces, one muted sage accent, rounded artwork,
slim neutral cover bodies, and fixed controller-focus indicators.

The visual reference is the public [TypeUI Glassmorphism guide](https://www.typeui.sh/design-skills/glassmorphism):
translucent structural panels, subtle edge light, clear typography, and readable
foregrounds. The registry landing page returned HTTP 429 during this work.
The full downloadable skill was not installed. This is a native, minimal
adaptation of the public guide, not its electric-blue palette or CSS blur stack.

## Implementation

- `itemzflow/include/ui_theme.h` defines shared color, radius, and type tokens.
- `GLES2_rects.cpp` uses the existing compiled solid-color shader for panels.
- `ui_geometry.h` builds 28 perimeter vertices without heap allocation or trigonometry.
- Glass panels use three draws: high-opacity fill, hairline border, and top-edge light.
  This is a simulated liquid-glass treatment, not optical refraction or backdrop blur.
- Cards use 12 px radii; container panels use 20 px radii.
- Artwork uses a rounded mesh cached at scene initialization, without new textures.
  Missing-icon fallback and missing-app warnings remain supported.
- Font sizes are 32 / 24 / 20 px. The default uses the already bundled Helvetica World;
  custom fonts and existing language-specific fonts still take precedence.
- The default background is static. Custom background images and shader binaries
  still work. Reflections are off by default, but saved `Reflections` values remain respected.
- The redesign adds no runtime libraries, framebuffer captures, blur passes, or shader binaries.

## Checks

Run the host-only geometry test from the repository root:

```sh
c++ -std=c++17 -Wall -Wextra -Werror itemzflow/tests/ui_geometry_test.cpp -o /tmp/opencode/itemzflow-ui-test
/tmp/opencode/itemzflow-ui-test
python3 itemzflow/tests/ui_render_test.py
python3 itemzflow/tests/ui_render_test.py --sdk "$ORBISDEV"
```

This test checks geometry bounds, winding, radius clamping, reversed coordinates,
degenerate rectangles, artwork geometry, and screen sizes. It does not validate
PS4 shader linkage, GPU performance, or the rendered interface.
The host GL-stub test compiles the exact drawing helper bodies and checks draw
counts, zero-opacity/degenerate panels, and helper GL-call cleanup. It is not a
replacement for a full SDK build. Browser-based Design QA tools cannot scan this
C++ interface; rendered QA remains a console task.
The `--sdk` mode syntax-checks these helpers with the actual PS4 vector types;
GL calls remain mocked, so it still does not prove rendered appearance.

The PS4 build needs the project's OrbisDev SDK and libraries. The official
Linux development release has been installed at `~/.local/opt/orbisdev`.
The SDK tools are appended to the user's PATH; the Makefile selects the SDK
compiler explicitly, leaving the system compiler unchanged.

For the current Fish terminal, load the new configuration:

```fish
source ~/.config/fish/conf.d/orbisdev.fish
```

For Bash or a POSIX shell:

```sh
. "$HOME/.config/orbisdev/env.sh"
```

Then build:

```sh
make -C itemzflow
```

The missing font engine, `orbisGl`, TagLib, dumper, PNG, and compression libraries
have now been built and installed in the user's SDK. The packaging tool has been
rebuilt for .NET 10. See [Build environment](build-environment.md) for exact sources,
SDK fixes, checks, and remaining blockers. OpenOrbis is not a drop-in replacement
for this OrbisDev build.

Checks in the current environment:

- Host geometry test: passed.
- Host drawing-helper test: passed, including client-memory/VBO handling.
- Geometry syntax check with the installed PS4 Clang 14.0.3: passed.
- Drawing-helper syntax check with the actual PS4 vector types: passed.
- Modified UI translation units: compiled successfully with PS4 Clang 14.0.3 and `-Werror`.
- Palette checks: text/metadata/accent exceed 4.5:1 on the defined surfaces;
  token contrast is not a rendered accessibility audit.
- `git diff --check`: passed.
- Full OrbisDev build: blocked by the pre-existing dumper API mismatch in
  `itemzflow/source/sig_handler.cpp`: `Dumper_Options` has no `sb_copy` member.
- Link dependencies: some project-specific OrbisDev libraries/stubs are still missing.
- Console appearance and GPU performance: not yet verified.

Before release, check on console:

- Home coverflow: several games, a single game, missing artwork, and an inserted disc.
- Game options and settings: controller focus, page changes, and long translated labels.
- File browser: both panels, directory changes, empty folders, and selected rows.
- Notifications: enter/exit animation, long messages, and warning/error icons.
- Themes: bright images, shader themes, custom fonts, and saved reflections enabled.
- Idle screen: static default background and existing screensaver information.
- Frame time and memory against the original build. Target no measurable regression;
  performance is unverified until measured on the console.
