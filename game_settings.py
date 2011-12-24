from utilities.vector import Vector

map_size = Vector(500,500)

human_count = 2
ai_count = 0
player_count = human_count + ai_count

eater_count = int((player_count + 1) / 2)
target_count = int((player_count + 1) / 2)

target_timeout = 5
target_size = 20

player_life = 10
bite_damage = 1
player_radius = 30
player_mass = 1
maximum_velocity = 10
maximum_acceleration = maximum_velocity / 2

friction_coefficient = 1/2
