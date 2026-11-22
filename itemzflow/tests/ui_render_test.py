#!/usr/bin/env python3
"""Compile the exact drawing helpers with a host GL stub; no PS4 SDK needed.

This checks helper geometry, draw budgets, and GL-call cleanup, not the actual
driver, full application build, or visual appearance.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--sdk", type=Path, help="Syntax-check with OrbisDev and its actual vector types; do not execute a PS4 binary")
args = parser.parse_args()

root = Path(__file__).resolve().parents[1]
source = (root / "source/GLES2_rects.cpp").read_text()
helpers = source[source.index("void ORBIS_RenderRoundedRect("):source.index("/* draw filling color bar */")]
header = (root / "include/GLES2_common.h").read_text()
start = header.index("void ORBIS_RenderRoundedRect(")
declaration = header[start:header.index(";", start) + 1]
stub = r'''
#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>
using GLuint = unsigned;
using GLint = int;
using GLfloat = float;
struct vec2 { float x, y; };
struct vec4 { union { struct { float x, y, z, w; }; struct { float r, g, b, a; }; }; };
#include "ui_theme.h"
#include "ui_geometry.h"
constexpr int USE_COLOR = 0, GL_BLEND = 1, GL_FUNC_ADD = 2,
              GL_SRC_ALPHA = 3, GL_ONE_MINUS_SRC_ALPHA = 4,
              GL_FLOAT = 5, GL_FALSE = 0, GL_LINE_LOOP = 6, GL_TRIANGLE_FAN = 7, GL_ARRAY_BUFFER = 8;
vec2 resolution = {1920, 1080};
GLuint glsl_Program[] = {1};
GLint solid_position_location = 0, solid_color_location = 0;
bool blending = false, attribute = false;
GLuint program = 0;
GLuint array_buffer = 99;
const float *vertices = nullptr;
std::vector<int> modes;
void glUseProgram(GLuint p) { program = p; }
void glEnable(int) { blending = true; }
void glDisable(int) { blending = false; }
void glBlendEquation(int) {}
void glBlendFunc(int, int) {}
void glBindBuffer(int target, GLuint buffer) { assert(target == GL_ARRAY_BUFFER); array_buffer = buffer; }
void glVertexAttribPointer(int, int, int, int, int, const void *v) {
    assert(array_buffer == 0);
    vertices = static_cast<const float *>(v);
}
void glEnableVertexAttribArray(int) { attribute = true; }
void glDisableVertexAttribArray(int) { attribute = false; }
void glUniform4f(int, float, float, float, float alpha) { assert(alpha >= 0 && alpha <= 1); }
void glDrawArrays(int mode, int, int count) {
    assert(blending && attribute && program == 1);
    assert(count == (mode == GL_LINE_LOOP ? 28 : 30));
    for (int i = 0; i < count * 2; ++i) assert((std::isfinite)(vertices[i]));
    modes.push_back(mode);
}
'''
checks = r'''
int main() {
    const vec4 rect = {-0.8f, -0.6f, 0.8f, 0.6f};
    ORBIS_RenderRoundedRect(ui_theme::surface, rect, 12, false);
    assert(modes.size() == 1 && modes[0] == GL_TRIANGLE_FAN);
    assert(!blending && !attribute && program == 0);
    modes.clear();
    GLES2_DrawGlassPanel(rect, 1);
    assert(modes.size() == 3 && modes[1] == GL_LINE_LOOP);
    modes.clear();
    GLES2_DrawGlassPanel(rect, 0);
    assert(modes.empty());
    GLES2_DrawGlassPanel(rect, -1);
    assert(modes.empty());
    GLES2_DrawGlassPanel(rect, 2);
    assert(modes.size() == 3);
    modes.clear();
    GLES2_DrawFocusCard(rect);
    assert(modes.size() == 3);
    modes.clear();
    const vec4 empty = {0, 0, 0, 0};
    GLES2_DrawGlassPanel(empty, 1);
    GLES2_DrawFocusCard(empty);
    assert(modes.empty());
    resolution = {0, 0};
    GLES2_DrawGlassPanel(rect, 1);
    GLES2_DrawFocusCard(rect);
    assert(modes.empty());
    assert(!blending && !attribute && program == 0);
    std::cout << "UI drawing helpers: all checks passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix="itemzflow-ui-", dir="/tmp/opencode") as directory:
    test_source = Path(directory) / "render.cpp"
    executable = Path(directory) / "render-test"
    if args.sdk:
        sdk = args.sdk.expanduser().resolve()
        stub = stub.replace("struct vec2 { float x, y; };\nstruct vec4 { union { struct { float x, y, z, w; }; struct { float r, g, b, a; }; }; };",
                            '#include "vec234.h"')
    test_source.write_text(stub + declaration + "\n" + helpers + checks)
    if args.sdk:
        subprocess.run([str(sdk / "bin/clang++"), "-std=c++17", "-Wall", "-Wextra", "-Werror",
                        "--target=x86_64-scei-ps4", "-isysroot", str(sdk),
                        "-isystem", str(sdk / "usr/include/c++/v1"),
                        "-isystem", str(sdk / "usr/include"),
                        "-I", str(sdk / "usr/include/orbis/freetype-gl"),
                        "-I", str(root / "include"), "-fsyntax-only", str(test_source)], check=True)
        print("UI drawing helpers: PS4 SDK syntax check passed (actual vector types, mock GL)")
    else:
        subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                        "-I", str(root / "include"), str(test_source), "-o", str(executable)], check=True)
        subprocess.run([str(executable)], check=True)
