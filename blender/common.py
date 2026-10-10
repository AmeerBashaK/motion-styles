import bpy, math, os

OUT = r"C:\Users\basha\Motion Design\WebBuilding\motion-styles\blender\frames"
FRAMES = 180  # 6 s @ 30 fps, every scene loops on this period


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, FRAMES
    sc.render.fps = 30
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.resolution_percentage = 100
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    try:
        sc.eevee.taa_render_samples = 32
    except AttributeError:
        pass
    sc.view_settings.view_transform = "Standard"
    return sc


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def mat(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexcol(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = hexcol(emit)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def world_color(color, strength=1.0):
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hexcol(color)
    bg.inputs["Strength"].default_value = strength
    return w


def camera(loc, rot_deg, lens=50, ortho_scale=None):
    bpy.ops.object.camera_add(location=loc, rotation=[math.radians(a) for a in rot_deg])
    cam = bpy.context.object
    if ortho_scale:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho_scale
    else:
        cam.data.lens = lens
    bpy.context.scene.camera = cam
    return cam


def linear_fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    try:
        curves = ad.action.fcurves
    except AttributeError:  # Blender 5 layered actions
        curves = [fc for layer in ad.action.layers for strip in layer.strips
                  for bag in strip.channelbags for fc in bag.fcurves]
    for fc in curves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def render(name):
    sc = bpy.context.scene
    folder = os.path.join(OUT, name)
    os.makedirs(folder, exist_ok=True)
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = os.path.join(folder, "f_")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(OUT), name + ".blend"))
    preview = os.environ.get("PREVIEW_FRAME")
    if preview:  # quick look: one still instead of the whole loop
        sc.frame_set(int(preview))
        sc.render.filepath = os.path.join(OUT, name + "_preview.png")
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
