#include "../include/ui_geometry.h"
#include <cassert>
#include <cmath>
#include <iostream>

static void check(float x0, float y0, float x1, float y1, float radius)
{
    const auto points = ui_geometry::rounded_perimeter(x0, y0, x1, y1, radius);
    const float left = std::min(x0, x1), right = std::max(x0, x1);
    const float bottom = std::min(y0, y1), top = std::max(y0, y1);
    float area = 0.0f;
    for (size_t i = 0; i < points.size(); ++i) {
        const auto &p = points[i];
        const auto &q = points[(i + 1) % points.size()];
        assert(std::isfinite(p.x) && std::isfinite(p.y));
        assert(p.x >= left - 0.001f && p.x <= right + 0.001f);
        assert(p.y >= bottom - 0.001f && p.y <= top + 0.001f);
        area += p.x * q.y - q.x * p.y;
    }
    if (left != right && top != bottom) assert(area > 0.0f);
    const auto reversed = ui_geometry::rounded_perimeter(x1, y1, x0, y0, radius);
    for (size_t i = 0; i < points.size(); ++i) {
        assert(points[i].x == reversed[i].x);
        assert(points[i].y == reversed[i].y);
    }
}

int main()
{
    check(0, 0, 1920, 1080, 0); // static canvas
    check(100, 100, 460, 240, 12); // card
    check(460, 240, 100, 100, 20); // negative-height layout panel
    check(0, 0, 100, 5, 100); // clamp to pill radius
    check(0, 0, 100, 5, -10); // negative radius
    check(0, 0, 0, 0, 20); // degenerate geometry (renderer skips it)
    check(-0.47f, -0.59f, 0.47f, 0.59f, 0.035f); // artwork mesh
    for (int width : {1280, 1920, 3840}) {
        const auto points = ui_geometry::rounded_perimeter(0, 0, width, width * 0.5625f, 12);
        assert(std::abs(points[0].x - width) < 0.001f);
        assert(std::abs(points[6].y - width * 0.5625f) < 0.001f);
    }
    std::cout << "UI geometry: all checks passed\n";
}
