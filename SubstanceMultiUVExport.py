import bpy

bl_info = {
    "name": "Substance Multi-UV Export",
    "blender": (2, 80, 0),
    "category": "Object",
    "author": "Sacred",
    "location": "View3D > Sidebar > Substance Multi-UV Export",
    "description": "Creates duplicate meshes for every UV map and every material of the selected meshes."
}

bpy.types.Scene.mesh_offset = bpy.props.FloatProperty(
    name = "Mesh Offset",
    description = "Distance between output meshes",
    default = -2.0,
    min = -100.0,
    max = 100.0
)
bpy.types.Scene.mesh_offset_axis = bpy.props.EnumProperty(
    name = "Offset Axis",
    description = "Axis to stack output meshes on",
    items=[
        ('X', "X", "Select X axis"),
        ('Y', "Y", "Select Y axis"),
        ('Z', "Z", "Select Z axis"),
    ],
    default='X'  # Set the default selection axis here
)


def ProcessMeshes(op, mesh_offset, mesh_offset_axis):

    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    # Check if any objects are selected
    if not selected_objects:

        # Check if an active collection exists
        if bpy.context.collection:
            for obj in bpy.context.collection.objects:
                if obj.type == 'MESH':
                    obj.select_set(True)
            selected_objects = bpy.context.selected_objects
        else:
            op.report({'WARNING'}, "No objects selected for processing.")
            return []
    
    processed_objects = [] # Store processed objects
    processed_collections = [] #Store processed object collections

    # Iterate over selected objects
    for obj in selected_objects:
        if obj.type == 'MESH':
            # Get the number of UV maps
            num_uv_maps = len(obj.data.uv_layers)
            
            if num_uv_maps > 1:
                processed_collection = bpy.data.collections.new(obj.name + "_Processed")
                processed_collections.append(processed_collection) 
                if len(obj.users_collection) > 0:                
                    collection = obj.users_collection[0]
                    collection.children.link(processed_collection)

                # Create a new mesh with a single UV map for each UV map in the original
                index = 0
                for uv_layer in obj.data.uv_layers:
                    # Create a new mesh with a single UV map
                    new_obj = bpy.data.objects.new(f"{obj.name}_{uv_layer.name}", obj.data.copy())
                    
                    # Link the new object to the collection
                    bpy.context.collection.objects.link(new_obj)
                    
                    # Apply a position offset on the specified axis                    
                    offset = index * mesh_offset

                    if mesh_offset_axis == "X":
                        new_obj.location.x += offset
                    elif mesh_offset_axis == "Y":
                        new_obj.location.y += offset    
                    else:
                        new_obj.location.z += offset

                    index += 1                 

                    # Remove all UV maps except the current one
                    uv_to_remove = []

                    for uv_map in new_obj.data.uv_layers:
                        if uv_map.name != uv_layer.name:
                            uv_to_remove.append(uv_map.name)
                    
                    for uv_map in uv_to_remove:
                        new_obj.data.uv_layers.remove(new_obj.data.uv_layers[uv_map])

                    # Create a list to store the new single-user materials
                    new_materials = []

                    # Replace materials on copies with new materials
                    for material in new_obj.data.materials:
                        new_material_name = f"{material.name}_{uv_layer.name}"
                    
                        # If material already exists in project, use existing one,
                        # otherwise create copy material from original mesh
                        if new_material_name in bpy.data.materials:
                            new_materials.append(bpy.data.materials[new_material_name])
                        else:
                            new_material = material.copy()
                            new_material.name = new_material_name
                            new_materials.append(new_material)

                    for i in range(len(new_obj.data.materials)):
                        new_obj.data.materials[i] = new_materials[i]


                    for i in range(len(new_obj.users_collection)):
                        new_obj.users_collection[i].objects.unlink(new_obj)
                    processed_collection.objects.link(new_obj)
                    processed_objects.append(new_obj)

    # Push to undo 
    bpy.ops.ed.undo_push(message = "Process Meshes")

    op.report({'INFO'}, f"Processed {len(processed_objects)} objects.")
    return processed_collections


def ExportMeshes():
    bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
        filepath='',
        check_existing=False,
        use_selection=True,
        object_types={'MESH'},
        apply_scale_options='FBX_SCALE_ALL',
        add_leaf_bones=False,
        bake_anim=False)


class ExportSelectedAsFBXOperator(bpy.types.Operator):
    bl_idname = "object.export_selected_as_fbx"
    bl_label = "Export Selected as FBX"
    
    def execute(self, context):
        # Get the selected objects
        selected_objects = bpy.context.selected_objects

        # Check if any objects are selected
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected for export.")
            return {'CANCELLED'}
        
        # Invoke the standard FBX export operator
        ExportMeshes()

        return {'FINISHED'}
    
    
class ProcessMeshesAndExport(bpy.types.Operator):
    bl_idname = "object.process_meshes_and_export"
    bl_label = "Process Meshes and Export"
    
    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, mesh_offset, mesh_offset_axis)
        if collections == []:
            return {'CANCELLED'}
        
        # Deselect all objects, then select only objects from processed collection
        bpy.ops.object.select_all(action='DESELECT')
        for collection in collections:
            for object in collection.objects:
                object.select_set(True)

        # Invoke the standard FBX export operator
        ExportMeshes()

        # bpy.ops.object.delete() Not possible to do export callbacks
        return {'FINISHED'}
    
    
class ProcessMeshesOperator(bpy.types.Operator):
    bl_idname = "object.process_meshes"
    bl_label = "Process Meshes"
    
    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, mesh_offset, mesh_offset_axis)

        if collections == []:
            return {'CANCELLED'}
        return {'FINISHED'}
        

class CustomPanel(bpy.types.Panel):
    bl_label = "Substance Multi-UV Export"
    bl_idname = "PT_SubstanceMultiUVExport"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Substance Multi-UV Export' # Tab name

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'mesh_offset')
        layout.prop(context.scene, 'mesh_offset_axis')
        layout.operator("object.export_selected_as_fbx")
        layout.operator("object.process_meshes")
        layout.operator("object.process_meshes_and_export")

def register():
    bpy.utils.register_class(ExportSelectedAsFBXOperator)
    bpy.utils.register_class(CustomPanel)
    bpy.utils.register_class(ProcessMeshesOperator)
    bpy.utils.register_class(ProcessMeshesAndExport)    

def unregister():
    bpy.utils.unregister_class(ExportSelectedAsFBXOperator)
    bpy.utils.unregister_class(CustomPanel)
    bpy.utils.unregister_class(ProcessMeshesOperator)
    bpy.utils.unregister_class(ProcessMeshesAndExport)

if __name__ == "__main__":
    register()