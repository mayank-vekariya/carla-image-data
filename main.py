import carla
import time
import os

def save_image(image, camera_name):
    image_folder = f"./output/{camera_name}"
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    image.save_to_disk(os.path.join(image_folder, f"{image.frame}.png"))


def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    actor_list = []

    try:
        world = client.get_world()
        blueprint_library = world.get_blueprint_library()

        # Assuming your vehicle is the first actor of type 'vehicle.*'
        vehicle = next(filter(lambda x: x.type_id.startswith('vehicle.'), world.get_actors()), None)

        if vehicle is None:
            print("Vehicle not found. Make sure the vehicle is spawned.")
            return

        # Attach cameras dynamically based on the vehicle's dimensions
        attach_dynamic_cameras(vehicle, world, actor_list)

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print('Destroying actors.')
        for actor in actor_list:
            if actor is not None:
                actor.destroy()
        print('Done capturing images.')


def attach_dynamic_cameras(vehicle, world, actor_list):
    # Get the bounding box of the vehicle (to adjust camera positions dynamically)
    bounding_box = vehicle.bounding_box
    vehicle_size = bounding_box.extent.x, bounding_box.extent.y, bounding_box.extent.z

    # Calculate camera positions based on the vehicle size
    camera_transforms = {
        'Front': carla.Transform(carla.Location(x=vehicle_size[0] * 1.5, z=vehicle_size[2]), carla.Rotation(yaw=0)),
        'Back': carla.Transform(carla.Location(x=-vehicle_size[0] * 1.5, z=vehicle_size[2]), carla.Rotation(yaw=180)),
        'Front Left': carla.Transform(carla.Location(x=vehicle_size[0], y=-vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=45)),
        'Front Right': carla.Transform(carla.Location(x=vehicle_size[0], y=vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=-45)),
        'Back Left': carla.Transform(carla.Location(x=-vehicle_size[0], y=-vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=135)),
        'Back Right': carla.Transform(carla.Location(x=-vehicle_size[0], y=vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=-135)),
    }

    blueprint_library = world.get_blueprint_library()
    camera_bp = blueprint_library.find('sensor.camera.rgb')

    # Attach cameras
    for name, transform in camera_transforms.items():
        camera_bp.set_attribute('image_size_x', '800')
        camera_bp.set_attribute('image_size_y', '600')
        camera_bp.set_attribute('fov', '110')
        camera = world.spawn_actor(camera_bp, transform, attach_to=vehicle)
        actor_list.append(camera)  # Keep track of camera actors for cleanup
        camera.listen(lambda image, name=name: save_image(image, name))



if __name__ == '__main__':
    main()
