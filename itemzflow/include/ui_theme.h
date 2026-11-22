#pragma once

// Shared visual tokens. Include after the GLES2 vector types are available.
namespace ui_theme {
inline const vec4 background = {0.071f, 0.082f, 0.090f, 1.0f}; // #121517
inline const vec4 surface = {0.125f, 0.145f, 0.153f, 1.0f};
inline const vec4 glass = {0.102f, 0.122f, 0.133f, 0.94f};
inline const vec4 border = {0.82f, 0.88f, 0.86f, 0.18f};
inline const vec4 sheen = {0.90f, 0.95f, 0.93f, 0.24f};
inline const vec4 accent = {0.66f, 0.78f, 0.73f, 1.0f}; // muted sage
inline const vec4 selected = {0.19f, 0.25f, 0.23f, 1.0f};
inline const vec4 text = {0.93f, 0.94f, 0.93f, 1.0f};
inline const vec4 muted = {0.66f, 0.71f, 0.70f, 1.0f};
inline const vec4 success = {0.59f, 0.78f, 0.65f, 1.0f};
inline const vec4 warning = {0.88f, 0.74f, 0.49f, 1.0f};
inline const vec4 danger = {0.91f, 0.60f, 0.59f, 1.0f};
inline constexpr float card_radius = 12.0f;
inline constexpr float panel_radius = 20.0f;
inline constexpr int title_size = 32;
inline constexpr int body_size = 24;
inline constexpr int detail_size = 20;
} // namespace ui_theme
