import bpy, math, sys, os, random
sys.path.append(os.path.dirname(__file__))
from common import *

sc = reset()
world_color("#EEF1F7", 1.0)
random.seed(7)

palette = ["#5B8DEF", "#F2B84B", "#EF6F6C", "#4FC3A1", "#9C7BEA"]

# base tile
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.25))
base = bpy.context.object; base.scale = (6.4, 6.4, 0.5)
base.data.materials.append(mat("Base", "#DDE3EE", rough=0.9))

# grid of blocks that drop in (staggered), hold, then lift out -> seamless loop
cells = [(x, y) for x in range(-2, 3) for y in range(-2, 3) if (x, y) not in ((0, 0), (2, -2), (-2, 2))]
random.shuffle(cells)
mats = [mat("C%d" % i, c, rough=0.8) for i, c in enumerate(palette)]
for i, (x, y) in enumerate(cells):
    h = random.choice((0.6, 1.0, 1.4, 2.2))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * 1.2, y * 1.2, h / 2))
    b = bpy.context.object; b.scale = (1, 1, h)
    b.data.materials.append(random.choice(mats))
    rest = h / 2
    t_in = 2 + i * 2          # staggered drop-in
    t_out = 120 + i * 2       # staggered lift-out
    for f, z in ((1, rest + 12), (t_in, rest + 12), (t_in + 12, rest - 0.12), (t_in + 16, rest),
                 (t_out, rest), (t_out + 14, rest + 12), (FRAMES + 1, rest + 12)):
        b.location.z = z; b.keyframe_insert("location", index=2, frame=f)

# centre tower with a rotating roof (axis-aligned motion)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5)); tower = bpy.context.object; tower.scale = (1, 1, 3)
tower.data.materials.append(mats[0])
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.85, depth=0.8, location=(0, 0, 3.4)); roof = bpy.context.object
roof.data.materials.append(mats[2]); roof.rotation_euler = (0, 0, math.radians(45))
roof.keyframe_insert("rotation_euler", index=2, frame=1)
roof.rotation_euler = (0, 0, math.radians(45 + 360)); roof.keyframe_insert("rotation_euler", index=2, frame=FRAMES + 1)
linear_fcurves(roof)

# three-tone lighting from one sun
bpy.ops.object.light_add(type="SUN", location=(5, -3, 10))
sun = bpy.context.object; sun.data.energy = 3.5
sun.rotation_euler = (math.radians(35), math.radians(15), math.radians(30))

# true isometric orthographic camera
cam = camera((14, -14, 14), (54.736, 0, 45), ortho_scale=15)

render("14-isometric")
