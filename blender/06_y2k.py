import bpy, math, sys, os
sys.path.append(os.path.dirname(__file__))
from common import *

sc = reset()

# world: banded gradient so chrome has something to reflect
w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
remap = nt.nodes.new("ShaderNodeMath"); remap.operation = "MULTIPLY_ADD"  # direction Z: -1..1 -> 0..1
remap.inputs[1].default_value = 0.5; remap.inputs[2].default_value = 0.5
nt.links.new(sep.outputs["Z"], remap.inputs[0])
nt.links.new(remap.outputs["Value"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
cr = ramp.color_ramp
stops = [(0.0, "#5B3BD6"), (0.33, "#7DF9FF"), (0.5, "#FFFFFF"), (0.6, "#FF8AD8"), (0.8, "#8A5CFF"), (1.0, "#2A1570")]
cr.elements[0].position, cr.elements[0].color = stops[0][0], hexcol(stops[0][1])
cr.elements[1].position, cr.elements[1].color = stops[-1][0], hexcol(stops[-1][1])
for p, c in stops[1:-1]:
    e = cr.elements.new(p); e.color = hexcol(c)
bg.inputs["Strength"].default_value = 1.2

chrome = mat("Chrome", "#FFFFFF", rough=0.06, metal=1.0)
irid = mat("Iridescent", "#C9B6FF", rough=0.12, metal=1.0)
try:
    ib = irid.node_tree.nodes["Principled BSDF"]
    ib.inputs["Thin Film Thickness"].default_value = 450
    ib.inputs["Thin Film IOR"].default_value = 1.6
except KeyError:
    pass

def spin(obj, axis, turns=1):
    obj.keyframe_insert("rotation_euler", index=axis, frame=1)
    r = list(obj.rotation_euler); r[axis] += math.radians(360 * turns); obj.rotation_euler = r
    obj.keyframe_insert("rotation_euler", index=axis, frame=FRAMES + 1)
    linear_fcurves(obj)

# hero: twisted chrome torus
bpy.ops.mesh.primitive_torus_add(major_radius=2.0, minor_radius=0.7, major_segments=96, minor_segments=32)
tor = bpy.context.object
tw = tor.modifiers.new("Twist", "SIMPLE_DEFORM"); tw.deform_method = "TWIST"; tw.angle = math.radians(180); tw.deform_axis = "Z"
sub = tor.modifiers.new("Sub", "SUBSURF"); sub.levels = sub.render_levels = 1
bpy.ops.object.shade_smooth()
tor.data.materials.append(chrome)
tor.rotation_euler = (math.radians(65), 0, 0)
spin(tor, 2)

# orbiting bubbles (iridescent)
for i in range(6):
    a = i / 6 * math.tau
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28 + 0.12 * (i % 3), location=(math.cos(a) * 3.6, math.sin(a) * 1.2, math.sin(a * 2) * 0.8))
    s = bpy.context.object; bpy.ops.object.shade_smooth()
    s.data.materials.append(irid if i % 2 else chrome)
    bpy.ops.object.empty_add(location=(0, 0, 0)); pivot = bpy.context.object
    s.parent = pivot
    pivot.rotation_euler = (math.radians(20), 0, a)
    spin(pivot, 2)

# 4-point sparkles (emission) that twinkle
sparkle = mat("Sparkle", "#FFFFFF", emit="#FFFFFF", emit_strength=12)
for i, (x, z) in enumerate(((-4.6, 2.2), (4.4, -1.8), (-3.2, -2.4), (3.6, 2.6))):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.05, depth=1.0, location=(x, -1, z))
    a = bpy.context.object; a.data.materials.append(sparkle)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.05, depth=1.0, location=(x, -1, z), rotation=(0, math.radians(90), 0))
    b = bpy.context.object; b.data.materials.append(sparkle); b.parent = a; b.location = (0, 0, 0); b.rotation_euler = (0, math.radians(90), 0)
    for j in range(7):
        f = 1 + j * 30 + i * 7
        k = 1.0 if j % 2 == 0 else 0.15
        a.scale = (k, k, k); a.keyframe_insert("scale", frame=f)

cam = camera((0, -17, 0), (90, 0, 0), lens=50)

# glare for the bloom-y Y2K look
sc.use_nodes = True
try:
    tree = sc.node_tree
    rl = tree.nodes.get("Render Layers") or tree.nodes.new("CompositorNodeRLayers")
    comp = tree.nodes.get("Composite") or tree.nodes.new("CompositorNodeComposite")
    gl = tree.nodes.new("CompositorNodeGlare"); gl.glare_type = "STREAKS"; gl.threshold = 0.9
    tree.links.new(rl.outputs["Image"], gl.inputs["Image"])
    tree.links.new(gl.outputs["Image"], comp.inputs["Image"])
except Exception as e:
    print("compositor skipped:", e)

render("06-y2k-chrome")


