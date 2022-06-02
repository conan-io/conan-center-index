/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#pragma once

#include <algorithm>
#include <span>
#include <tuple>

#include "SFML/Graphics.hpp"

#include "../core/ThreadPool.hpp"
#include "../graphics/Image.hpp"
#include "../graphics/Trail.hpp"
#include "../gui/Keyboard.hpp"
#include "../gui/Mouse.hpp"
#include "../math/BoundingBox.hpp"
#include "../math/Extents.hpp"
#include "../math/Transform.hpp"
#include "../math/vector_math.hpp"
#include "../physics/Particle.hpp"
#include "../util/FunctionRef.hpp"
#include "../util/Stopwatch.hpp"

namespace sm
{
enum class VertexMode
{
    Points,
    Lines,
    LineStrip,
    Triangles,
    TriangleStrip,
    TriangleFan,
    Quads
};


class App
{
    sf::RenderWindow sf_render_window;
    sf::Texture texture;
    Stopwatch watch{};
    u64 target_framerate;
    Image image;

  public:
    struct Settings
    {
        Dimensions dims{sm::dimsFHD};
        std::string name{"Samarium Window"};
        uint32_t framerate{64};
    };

    ThreadPool thread_pool{};
    Transform transform;
    u64 frame_counter{};
    Keymap keymap;
    Mouse mouse{sf_render_window};

    explicit App(const Settings& settings)
        : sf_render_window(
              sf::VideoMode(static_cast<u32>(settings.dims.x), static_cast<u32>(settings.dims.y)),
              settings.name,
              sf::Style::Titlebar | sf::Style::Close,
              sf::ContextSettings{0, 0, /* antialiasing factor */ 8}),
          target_framerate{settings.framerate}, image{settings.dims},
          transform{.pos   = image.dims.as<f64>() / 2.,
                    .scale = Vector2::combine(10) * Vector2{1.0, -1.0}}
    {
        texture.create(static_cast<u32>(settings.dims.x), static_cast<u32>(settings.dims.y));

        sf_render_window.setFramerateLimit(settings.framerate);

        keymap.push_back({Keyboard::Key::LControl, Keyboard::Key::Q}, // exit by default with Ctrl+Q
                         [&sf_render_window = this->sf_render_window]
                         { sf_render_window.close(); });
    }

    void load_pixels();

    void store_pixels();

    void display();

    auto is_open() const -> bool;

    void get_input();

    auto dims() const -> Dimensions;

    auto transformed_dims() const -> Vector2;

    auto bounding_box() const -> BoundingBox<size_t>;

    auto viewport_box() const -> std::array<LineSegment, 4>;

    auto get_image() const -> Image;

    void fill(Color color);

    void draw(Circle circle, Color color);

    void draw(const Particle& particle);

    void draw_line_segment(const LineSegment& ls,
                           Color color   = Color{255, 255, 255},
                           f64 thickness = 0.1);


    void draw_world_space(FunctionRef<Color(Vector2)> callable);
    void draw_world_space(FunctionRef<Color(Vector2)> callable,
                          const BoundingBox<f64>& bounding_box);

    void draw_polyline(std::span<const Vector2> vertices,
                       Color color   = Color{255, 255, 255},
                       f64 thickness = 1.0);

    void draw_polygon(std::span<const Vector2> vertices,
                       Color color   = Color{255, 255, 255},
                       f64 thickness = 1.0);

    void draw(Trail trail, Color color = Color{255, 255, 255}, f64 thickness = 1.0);

    void draw_vertices(std::span<const Vector2> vertices, VertexMode mode = VertexMode::LineStrip);

    void run(FunctionRef<void(f64)> update, FunctionRef<void()> draw, u64 substeps = 1UL);

    void run(FunctionRef<void()> func);
};
} // namespace sm
