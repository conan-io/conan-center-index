/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2022 Jai Bellare
 * See <https://opensource.org/licenses/MIT/> or LICENSE.md
 * Project homepage: https://github.com/strangeQuark1041/samarium
 */

#include "SFML/Graphics/CircleShape.hpp"
#include "SFML/Graphics/PrimitiveType.hpp"
#include "SFML/Graphics/Vertex.hpp"
#include "SFML/Graphics/VertexArray.hpp"

#include "../util/file.hpp"
#include "../util/format.hpp"
#include "../util/print.hpp"

#include "App.hpp"

namespace sm
{
void App::load_pixels()
{
    this->texture.update(this->sf_render_window);
    const auto sf_image = texture.copyToImage();
    const auto ptr      = sf_image.getPixelsPtr();

    std::copy(ptr, ptr + image.size() * 4UL, reinterpret_cast<u8*>(&image[0]));
}

void App::store_pixels()
{
    this->texture.update(reinterpret_cast<const u8*>(&image[0]));
    sf::Sprite sprite(texture);

    this->sf_render_window.draw(sprite);
}

void App::display()
{
    sf_render_window.display();
    frame_counter++;
    watch.reset();
}

void App::fill(Color color) { sf_render_window.clear(sfml(color)); }

auto App::is_open() const -> bool { return sf_render_window.isOpen(); }

void App::get_input()
{
    this->mouse.scroll_amount = 0.0;

    sf::Event event;
    while (sf_render_window.pollEvent(event))
    {
        if (event.type == sf::Event::Closed) { sf_render_window.close(); }
        else if (event.type == sf::Event::MouseWheelScrolled &&
                 event.mouseWheelScroll.wheel == sf::Mouse::VerticalWheel)
        {
            this->mouse.scroll_amount = static_cast<f64>(event.mouseWheelScroll.delta);
        }
    }

    this->keymap.run();
    this->mouse.update(this->sf_render_window);
}

auto App::dims() const -> Dimensions { return image.dims; }

auto App::transformed_dims() const -> Vector2 { return this->dims().as<f64>() / transform.scale; }

auto App::bounding_box() const -> BoundingBox<size_t> { return this->image.bounding_box(); }

auto App::viewport_box() const -> std::array<LineSegment, 4>
{
    const auto f64_dims = this->image.dims.as<f64>();

    return std::array{
        this->transform.apply_inverse(LineSegment{{}, {0.0, f64_dims.y}}),
        this->transform.apply_inverse(LineSegment{{}, {f64_dims.x, 0.0}}),
        this->transform.apply_inverse(LineSegment{{f64_dims.x, 0.0}, {f64_dims.x, f64_dims.y}}),
        this->transform.apply_inverse(LineSegment{{0.0, f64_dims.y}, {f64_dims.x, f64_dims.y}})};
}

auto App::get_image() const -> Image { return this->image; }

void App::draw(Circle circle, Color color)
{
    const auto radius   = circle.radius * transform.scale.x;
    const auto radius32 = static_cast<f32>(radius);
    const auto pos      = transform.apply(circle.centre).as<f32>();

    auto shape = sf::CircleShape{static_cast<f32>(radius)};
    shape.setFillColor(sfml(color));
    shape.setOrigin(radius32, radius32);
    shape.setPosition(pos.x, pos.y);

    sf_render_window.draw(shape);
}

void App::draw(const Particle& particle) { this->draw(particle.as_circle(), particle.color); }

void App::draw_line_segment(const LineSegment& ls, Color color, f64 thickness)
{
    const auto sfml_color = sfml(color);
    const auto thickness_vector =
        Vector2::from_polar({.length = thickness, .angle = ls.vector().angle() + math::pi / 2.0});

    auto vertices = std::array<sf::Vertex, 4>{};

    vertices[0].position = sfml(transform.apply(ls.p1 - thickness_vector).as<f32>());
    vertices[1].position = sfml(transform.apply(ls.p1 + thickness_vector).as<f32>());
    vertices[2].position = sfml(transform.apply(ls.p2 + thickness_vector).as<f32>());
    vertices[3].position = sfml(transform.apply(ls.p2 - thickness_vector).as<f32>());

    vertices[0].color = sfml_color;
    vertices[1].color = sfml_color;
    vertices[2].color = sfml_color;
    vertices[3].color = sfml_color;

    sf_render_window.draw(vertices.data(), vertices.size(), sf::Quads);
}

void App::draw_world_space(FunctionRef<Color(Vector2)> callable)
{
    const auto bounding_box    = image.bounding_box();
    const auto transformed_box = transform.apply_inverse(BoundingBox<u64>{
        .min = bounding_box.min,
        .max = bounding_box.max + Indices{1, 1}}.template as<f64>());

    this->draw_world_space(callable, transformed_box);
}

void App::draw_world_space(FunctionRef<Color(Vector2)> callable,
                           const BoundingBox<f64>& bounding_box)
{
    load_pixels();

    const auto box = this->transform.apply(bounding_box)
                         .clamped_to(image.bounding_box().template as<f64>())
                         .template as<u64>();

    if (math::area(box) == 0UL) { return; }

    const auto x_range = box.x_range();
    const auto y_range = box.y_range();

    const auto job = [&](auto min, auto max)
    {
        for (auto y : range(min, max))
        {
            for (auto x : x_range)
            {
                const auto coords = Indices{x, y};
                const auto col    = callable(transform.apply_inverse(coords.template as<f64>()));

                image[coords].add_alpha_over(col);
            }
        }
    };

    thread_pool.parallelize_loop(y_range.min, y_range.max + 1, job, thread_pool.get_thread_count());

    store_pixels();
}

void App::draw_polyline(std::span<const Vector2> vertices, Color color, f64 thickness)
{
    for (auto i : range(vertices.size() - 1UL))
    {
        draw_line_segment(LineSegment{vertices[i], vertices[i + 1UL]}, color, thickness);
    }
}

void App::draw_polygon(std::span<const Vector2> vertices, Color color, f64 thickness)
{
    for (auto i : range(vertices.size() - 1UL))
    {
        draw_line_segment(LineSegment{vertices[i], vertices[i + 1UL]}, color, thickness);
    }
    draw_line_segment(LineSegment{vertices.back(), vertices.front()}, color, thickness);
}

void App::draw_vertices(std::span<const Vector2> vertices, VertexMode mode)
{
    auto converted = sf::VertexArray(static_cast<sf::PrimitiveType>(mode), vertices.size());
    for (auto i : range(vertices.size())) { converted[i].position = sfml(vertices[i].as<f32>()); }
    sf_render_window.draw(converted);
}


void App::run(FunctionRef<void(f64)> update, FunctionRef<void()> draw, u64 substeps)
{
    while (this->is_open())
    {
        this->get_input();

        for (auto i : range(substeps))
        {
            std::ignore = i;
            update(1.0 / static_cast<f64>(substeps) / static_cast<f64>(this->target_framerate));
        }
        draw();

        this->display();
    }
}

void App::run(FunctionRef<void()> func)
{
    while (this->is_open())
    {
        this->get_input();
        func();
        this->display();
    }
}
} // namespace sm
