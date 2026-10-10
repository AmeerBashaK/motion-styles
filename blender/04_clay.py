import bpy, math, sys, os
sys.path.append(os.path.dirname(__file__))
from common import *

sc = reset()
world_color("#F7D9E3", 0.35)

def clay(name, color):
    m = mat(name, color, rough=0.85)
    b = m.node_tree.nodes["Principled BSDF"]
    try:
        b.inputs["Subsurface Weight"].default_value = 0.15
        b.inputs["Subsurface Radius"].default_value = (0.4, 0.2, 0.15)
    except KeyError:
        pass
    # fingerprint-ish bumps
    nt = m.node_tree
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 60
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m

def smooth(obj, levels=2):
    mod = obj.modifiers.new("Sub", "SUBSURF"); mod.levels = mod.render_levels = levels
    bpy.ops.object.shade_smooth()

# curved backdrop (cyclorama)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
floor = bpy.context.object
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="DESELECT")
bpy.ops.object.mode_set(mode="OBJECT")
for v in floor.data.vertices:
    if v.co.y > 0:
        v.select = True
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 15)})
bpy.ops.object.mode_set(mode="OBJECT")
bev = floor.modifiers.new("Bevel", "BEVEL"); bev.width = 4; bev.segments = 16
floor.data.materials.append(clay("Backdrop", "#F9C9D6"))
bpy.ops.object.shade_smooth()

# bouncing ball with squash & stretch (period 1 s = 30 frames)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-2.6, 0, 1))
ball = bpy.context.object; smooth(ball, 1)
ball.data.materials.append(clay("Ball", "#FF7A59"))
for cyc in range(7):
    f0 = 1 + cyc * 30
    for f, z, s in ((f0, 1.0, (1.25, 1.25, 0.65)), (f0 + 4, 1.4, (0.9, 0.9, 1.2)),
                    (f0 + 15, 3.4, (1, 1, 1)), (f0 + 26, 1.4, (0.9, 0.9, 1.2))):
        if f > FRAMES + 30:
            continue
        ball.location.z = z; ball.scale = s
        ball.keyframe_insert("location", index=2, frame=f)
        ball.keyframe_insert("scale", frame=f)

# rounded cube turning 360 over 6 s
bpy.ops.mesh.primitive_cube_add(size=1.8, location=(0.4, 0.6, 0.9))
cube = bpy.context.object
b2 = cube.modifiers.new("Bevel", "BEVEL"); b2.width = 0.35; b2.segments = 8
bpy.ops.object.shade_smooth()
cube.data.materials.append(clay("Cube", "#7AD3C1"))
cube.rotation_euler = (0, 0, 0); cube.keyframe_insert("rotation_euler", index=2, frame=1)
cube.rotation_euler = (0, 0, math.radians(360)); cube.keyframe_insert("rotation_euler", index=2, frame=FRAMES + 1)
linear_fcurves(cube)

# wobbling torus (jiggle) on the right
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.42, location=(3.0, 0.2, 1.3), rotation=(math.radians(70), 0, 0))
tor = bpy.context.object; smooth(tor, 1)
tor.data.materials.append(clay("Torus", "#FFD166"))
for i in range(0, 13):
    f = 1 + i * 15
    k = 1 + (0.08 if i % 2 else -0.08)
    tor.scale = (k, 2 - k, 1); tor.keyframe_insert("scale", frame=f)

# little purple bean resting
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(1.6, -1.6, 0.45))
bean = bpy.context.object; bean.scale = (1.4, 0.8, 0.75); smooth(bean, 1)
bean.data.materials.append(clay("Bean", "#9B8CFF"))

# soft miniature-set lighting
bpy.ops.object.light_add(type="AREA", location=(-4, -6, 9))
key = bpy.context.object; key.data.energy = 1400; key.data.size = 8
key.rotation_euler = (math.radians(45), 0, math.radians(-30))
bpy.ops.object.light_add(type="AREA", location=(6, -3, 4))
fill = bpy.context.object; fill.data.energy = 250; fill.data.size = 6
fill.rotation_euler = (math.radians(70), 0, math.radians(60))

cam = camera((0, -12, 4.2), (76, 0, 0), lens=45)
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 12; cam.data.dof.aperture_fstop = 2.8

render("04-clay-3d")


