import bpy
from math import radians

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

rib_length = 54
rib_height = 15
rib_width = 8

base_length = 72
base_width = 38
base_height = 8

wall_length = 8
wall_width = 38
wall_height = 60

cyl_length = 15
cyl_outer = 28
cyl_inner = 20

mesh = bpy.data.meshes.new("Rib")
rib = bpy.data.objects.new("Rib", mesh)
bpy.context.collection.objects.link(rib)
verts = [(0, 0, 0), (rib_length, 0, 0), (rib_length, 0, rib_height)]
faces = [(0, 1, 2)]
mesh.from_pydata(verts, [], faces)
mesh.update()
bpy.context.view_layer.objects.active = rib
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, rib_width, 0)})
bpy.ops.object.mode_set(mode='OBJECT')
rib.location = (-54, -4, 0)

bpy.ops.mesh.primitive_cube_add(size=1)
base = bpy.context.object
base.name = "Base"
base.scale = (base_length, base_width, base_height)
base.location = (-28, 0, -4)

bpy.ops.mesh.primitive_cube_add(size=1)
wall = bpy.context.object
wall.name = "Wall"
wall.scale = (wall_length, wall_width, wall_height)
wall.location = (4, 0, 30)

bpy.ops.mesh.primitive_cylinder_add(radius=cyl_outer/2, depth=cyl_length)
cyl_outer_obj = bpy.context.object
cyl_outer_obj.name = "OuterCyl"
cyl_outer_obj.rotation_euler[1] = radians(90)
cyl_outer_obj.location = (-7.5, 0, 44)

bpy.ops.object.select_all(action='DESELECT')
for obj in [rib, base, wall, cyl_outer_obj]:
    obj.select_set(True)

bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.select_all(action='DESELECT')

def bool_union(target, tool):
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_add(type='BOOLEAN')
    mod = target.modifiers[-1]
    mod.object = tool
    mod.operation = 'UNION'
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)

bool_union(base, wall)
bool_union(base, cyl_outer_obj)
bool_union(base, rib)

for obj in [wall, cyl_outer_obj, rib]:
    bpy.data.objects.remove(obj, do_unlink=True)

cutter_radius = cyl_inner / 2
cutter_depth = cyl_length + wall_length + 0.2
bpy.ops.mesh.primitive_cylinder_add(radius=cutter_radius, depth=cutter_depth)
cutter = bpy.context.object
cutter.name = "HoleCutter"
cutter.rotation_euler[1] = radians(90)
cutter.location = (-3.5, 0, 44)

bpy.ops.object.select_all(action='DESELECT')
cutter.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.select_all(action='DESELECT')

bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_add(type='BOOLEAN')
mod = base.modifiers[-1]
mod.object = cutter
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'
bpy.ops.object.modifier_apply(modifier=mod.name)

bpy.data.objects.remove(cutter, do_unlink=True)

