#include <threepp/threepp.hpp>

using namespace threepp;

auto createBox(const Vector3 &pos, const Color &color)
{
    auto geometry = BoxGeometry::create();
    auto material = MeshPhongMaterial::create();
    material->color = color;

    auto box = Mesh::create(geometry, material);
    box->position.copy(pos);

    return box;
}

auto createPlane()
{
    auto planeGeometry = PlaneGeometry::create(5, 5);
    auto planeMaterial = MeshLambertMaterial::create();
    planeMaterial->color = Color::gray;
    planeMaterial->side = Side::Double;

    auto plane = Mesh::create(planeGeometry, planeMaterial);
    plane->position.y = -1;
    plane->rotateX(math::degToRad(90));

    return plane;
}

int main()
{

    auto scene = Scene::create();
    auto light = HemisphereLight::create();
    scene->add(light);
    auto plane = createPlane();
    scene->add(plane);
    auto group = Group::create();
    group->add(createBox({-1, 0, 0}, Color::green));
    group->add(createBox({1, 0, 0}, Color::red));
    scene->add(group);
}
