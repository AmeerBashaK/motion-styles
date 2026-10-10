import bpy, math, sys, os, random
sys.path.append(os.path.dirname(__file__))
from common import *

sc = reset()
world_color("#1B2440", 1.0)
random.seed(3)

# planet: flat-shaded icosphere with displaced vertices
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=2.2)
land = bpy.context.object
for v in land.data.vertices:
    n = v.co.normalized()
    v.co = n * (2.2 + random.uniform(-0.06, 0.22))
bpy.ops.object.shade_flat()
land.data.materials.append(mat("Land", "#6BBF59", rough=1.0))

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.28)
sea = bpy.context.object; bpy.ops.object.shade_flat()
sea.data.materials.append(mat("Sea", "#3A86C8", rough=0.6))

# low-poly trees (cones) scattered on the land surface, parented to planet
leaf = mat("Leaf", "#2E7D4F", rough=1.0)
trunk_m = mat("Trunk", "#7A5230", rough=1.0)
for i in range(26):
    u, w = random.random(), random.random()
    th, ph = math.tau * u, math.acos(2 * w - 1)
    d = (math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph))
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.18, depth=0.55, location=[c * 2.55 for c in d])
    t = bpy.context.object; t.data.materials.append(leaf); bpy.ops.object.shade_flat()
    t.rotation_mode = "QUATERNION"
    from mathutils import Vector
    t.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d))
    t.parent = land

# clouds: flat low-poly blobs orbiting
cloud = mat("Cloud", "#F4F6FB", rough=1.0)
pivot_c = None
bpy.ops.object.empty_add(); pivot_c = bpy.context.object
for i in range(4):
    a = i / 4 * math.tau
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.28, location=(math.cos(a) * 3.0, math.sin(a) * 3.0, 0.6 - i * 0.4))
    c = bpy.context.object; c.scale = (1.6, 1, 0.7); bpy.ops.object.shade_flat()
    c.data.materials.append(cloud); c.parent = pivot_c
pivot_c.rotation_euler = (math.radians(15), 0, 0)
pivot_c.keyframe_insert("rotation_euler", index=2, frame=1)
pivot_c.rotation_euler = (math.radians(15), 0, math.radians(-360)); pivot_c.keyframe_insert("rotation_euler", index=2, frame=FRAMES + 1)
linear_fcurves(pivot_c)

# planet spin 360 over the loop
for o in (land, sea):
    o.rotation_euler = (math.radians(20), 0, 0); o.keyframe_insert("rotation_euler", index=2, frame=1)
    o.rotation_euler = (math.radians(20), 0, math.radians(360)); o.keyframe_insert("rotation_euler", index=2, frame=FRAMES + 1)
    linear_fcurves(o)

# low-poly moon
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45, location=(4.2, 1.5, 1.6))
moon = bpy.context.object; bpy.ops.object.shade_flat(); moon.data.materials.append(mat("Moon", "#F2E2B6", rough=1.0))

# stars
star = mat("Star", "#FFFFFF", emit="#FFFFFF", emit_strength=6)
for i in range(70):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.03,
                                          location=(random.uniform(-9, 9), 6, random.uniform(-5, 5)))
    bpy.context.object.data.materials.append(star)

bpy.ops.object.light_add(type="SUN"); s = bpy.context.object
s.data.energy = 3.2; s.rotation_euler = (math.radians(50), math.radians(-30), math.radians(-20))
bpy.ops.object.light_add(type="SUN"); r = bpy.context.object
r.data.energy = 0.6; r.data.color = hexcol("#7FA8FF")[:3]; r.rotation_euler = (math.radians(-60), math.radians(40), 0)

camera((0, -15, 0.6), (88, 0, 0), lens=50)
render("15-low-poly")

