#pragma once
#include <algorithm>
#include <array>

namespace ui_geometry {
struct Point { float x, y; };
using Perimeter = std::array<Point, 28>;

// Counter-clockwise, six segments per corner. No allocation or trigonometry
// in the render loop. Both endpoint orders and pill-sized radii are supported.
inline Perimeter rounded_perimeter(float x0, float y0, float x1, float y1, float radius)
{
    const float left = std::min(x0, x1), right = std::max(x0, x1);
    const float bottom = std::min(y0, y1), top = std::max(y0, y1);
    radius = std::max(0.0f, std::min(radius, std::min(right - left, top - bottom) * 0.5f));
    constexpr float cosine[] = {1.0f, 0.965926f, 0.866025f, 0.707107f, 0.5f, 0.258819f, 0.0f};
    constexpr float sine[] = {0.0f, 0.258819f, 0.5f, 0.707107f, 0.866025f, 0.965926f, 1.0f};
    Perimeter points{};
    for (int i = 0; i < 7; ++i) {
        const float c = cosine[i] * radius, s = sine[i] * radius;
        points[i] = {right - radius + c, top - radius + s};
        points[7 + i] = {left + radius - s, top - radius + c};
        points[14 + i] = {left + radius - c, bottom + radius - s};
        points[21 + i] = {right - radius + s, bottom + radius - c};
    }
    return points;
}
} // namespace ui_geometry
