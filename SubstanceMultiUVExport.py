import bpy

bl_info = {
    "name": "Substance Multi-UV Export",
    "blender": (2, 80, 0),
    "category": "Object",
    "author": "Sacred",
    "location": "View3D > Sidebar > Substance Multi-UV Export",
    "description": "Creates duplicate meshes for every UV map and every material of the selected meshes.",
}

bpy.types.Scene.mesh_offset = bpy.props.FloatProperty(
    name="Mesh Offset",
    description="Distance between output meshes",
    default=-2.0,
    min=-100.0,
    max=100.0,
)
bpy.types.Scene.mesh_offset_axis = bpy.props.EnumProperty(
    name="Offset Axis",
    description="Axis to stack output meshes on",
    items=[
        ("X", "X", "Select X axis"),
        ("Y", "Y", "Select Y axis"),
        ("Z", "Z", "Select Z axis"),
    ],
    default="Z",  # Set the default selection axis here
)


def ProcessMeshes(op, mode, mesh_offset, mesh_offset_axis):
    # Get the selected objects
    selected_objects = bpy.context.selected_objects

    # Check if any objects are selected
    if not selected_objects:
        # Check if an active collection exists
        if bpy.context.collection:
            for obj in bpy.context.collection.objects:
                if obj.type == "MESH":
                    obj.select_set(True)
            selected_objects = bpy.context.selected_objects
        else:
            op.report({"WARNING"}, "No objects selected for processing.")
            return []

    processed_objects = []  # Store processed objects
    processed_collections = []  # Store processed object collections

    # Iterate over selected objects
    for obj in selected_objects:
        if obj.type == "MESH":
            if mode == "multiuv":
                print("Multi UV")
                # Get the number of UV maps
                num_uv_maps = len(obj.data.uv_layers)

                if num_uv_maps > 1:
                    processed_collection = bpy.data.collections.new(
                        obj.name + "_Processed"
                    )
                    processed_collections.append(processed_collection)
                    if len(obj.users_collection) > 0:
                        collection = obj.users_collection[0]
                        collection.children.link(processed_collection)

                    # Create a new mesh with a single UV map for each UV map in the original
                    index = 0
                    for uv_layer in obj.data.uv_layers:
                        # Create a new mesh with a single UV map
                        new_obj = bpy.data.objects.new(
                            f"{obj.name}_{uv_layer.name}", obj.data.copy()
                        )

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
                            new_obj.data.uv_layers.remove(
                                new_obj.data.uv_layers[uv_map]
                            )

                        # Create a list to store the new single-user materials
                        new_materials = []

                        # Replace materials on copies with new materials
                        for material in new_obj.data.materials:
                            new_material_name = f"{material.name}_{uv_layer.name}"

                            # If material already exists in project, use existing one,
                            # otherwise create copy material from original mesh
                            if new_material_name in bpy.data.materials:
                                new_materials.append(
                                    bpy.data.materials[new_material_name]
                                )
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

            elif mode == "uvtile":
                # get the amount of materials
                materials = obj.data.materials
                num_materials = len(materials)
                if num_materials == 1:
                    op.report({"WARNING"}, "Mesh(es) only have one material.")
                    return
                if num_materials > 16:
                    op.report({"WARNING"}, "Mesh(es) have more than 16 materials.")
                    return

                op.report({"INFO"}, f"{num_materials} materials")

                if obj.data.uv_layers.active:
                    # Create a new mesh with a single material
                    new_obj = bpy.data.objects.new(
                        f"{obj.name}_uvtiles", obj.data.copy()
                    )

                    # Link the new object to the collection
                    bpy.context.collection.objects.link(new_obj)
                    uv_layer = new_obj.data.uv_layers.active.data

                    processed_collection = bpy.data.collections.new(
                        obj.name + "_uvtiles"
                    )
                    processed_collections.append(processed_collection)
                    if len(new_obj.users_collection) > 0:
                        collection = new_obj.users_collection[0]
                        collection.children.link(processed_collection)

                    # Group faces by material index
                    material_faces = {}
                    for poly in new_obj.data.polygons:
                        material_index = poly.material_index
                        if material_index not in material_faces:
                            material_faces[material_index] = []
                        material_faces[material_index].extend(poly.loop_indices)

                    # Offset UVs for each material index
                    for material_index, loop_indices in material_faces.items():
                        offset_factor = (
                            material_index  # Adjust the offset factor as needed
                        )
                        for loop_index in loop_indices:
                            x_offset = offset_factor % 4
                            y_offset = offset_factor // 4

                            uv_layer[loop_index].uv.x += x_offset
                            uv_layer[loop_index].uv.y += y_offset

                    new_material_name = f"{new_obj.name}"

                    # If material already exists in project, use existing one,
                    # otherwise create copy material from original mesh
                    if new_material_name in bpy.data.materials:
                        new_material = bpy.data.materials[new_material_name]
                    else:
                        new_material = bpy.data.materials.new(name=new_material_name)

                    new_obj.data.materials.clear()
                    new_obj.data.materials.append(new_material)

                    for i in range(len(new_obj.users_collection)):
                        new_obj.users_collection[i].objects.unlink(new_obj)
                    processed_collection.objects.link(new_obj)
                    processed_objects.append(new_obj)

    # Push to undo
    bpy.ops.ed.undo_push(message="Process Meshes")

    op.report({"INFO"}, f"Processed {len(processed_objects)} objects.")
    return processed_collections


def ExportMeshes():
    bpy.ops.export_scene.fbx(
        "INVOKE_DEFAULT",
        filepath="",
        check_existing=False,
        use_selection=True,
        object_types={"MESH"},
        apply_scale_options="FBX_SCALE_ALL",
        add_leaf_bones=False,
        bake_anim=False,
    )


class ExportSelectedAsFBXOperator(bpy.types.Operator):
    bl_idname = "object.export_selected_as_fbx"
    bl_label = "Export Selected as FBX"

    def execute(self, context):
        # Get the selected objects
        selected_objects = bpy.context.selected_objects

        # Check if any objects are selected
        if not selected_objects:
            self.report({"WARNING"}, "No objects selected for export.")
            return {"CANCELLED"}

        # Invoke the standard FBX export operator
        ExportMeshes()

        return {"FINISHED"}


class MultiUVProcess(bpy.types.Operator):
    bl_idname = "object.multiuv_process"
    bl_label = "Process Meshes"

    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, "multiuv", mesh_offset, mesh_offset_axis)

        if collections == []:
            return {"CANCELLED"}
        return {"FINISHED"}


class MultiUVProcessAndExport(bpy.types.Operator):
    bl_idname = "object.multiuv_process_and_export"
    bl_label = "Process Meshes and Export"

    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, "multiuv", mesh_offset, mesh_offset_axis)
        if collections == []:
            return {"CANCELLED"}

        # Deselect all objects, then select only objects from processed collection
        bpy.ops.object.select_all(action="DESELECT")
        for collection in collections:
            for object in collection.objects:
                object.select_set(True)

        # Invoke the standard FBX export operator
        ExportMeshes()

        # bpy.ops.object.delete() Not possible to do export callbacks
        return {"FINISHED"}


class UVTileProcess(bpy.types.Operator):
    bl_idname = "object.uvtile_process"
    bl_label = "Process Meshes"

    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, "uvtile", mesh_offset, mesh_offset_axis)

        if collections == []:
            return {"CANCELLED"}
        return {"FINISHED"}


class UVTileProcessAndExport(bpy.types.Operator):
    bl_idname = "object.uvtile_process_and_export"
    bl_label = "Process Meshes and Export"

    def execute(self, context):
        mesh_offset = context.scene.mesh_offset
        mesh_offset_axis = context.scene.mesh_offset_axis
        collections = ProcessMeshes(self, "uvtile", mesh_offset, mesh_offset_axis)
        if collections == []:
            return {"CANCELLED"}

        # Deselect all objects, then select only objects from processed collection
        bpy.ops.object.select_all(action="DESELECT")
        for collection in collections:
            for object in collection.objects:
                object.select_set(True)

        # Invoke the standard FBX export operator
        ExportMeshes()

        # bpy.ops.object.delete() Not possible to do export callbacks
        return {"FINISHED"}


class BasePanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Substance Multi-UV Export"
    # bl_options = {"DEFAULT_OPENED"}


# class RootPanel(BasePanel, bpy.types.Panel):
#     bl_label = "Substance Multi-UV Export"
#     bl_idname = "RootPanel"
#     def draw(self, context):
#         layout = self.layout
#         layout.label(text="Substance Multi-UV Export")


class Utilities(BasePanel, bpy.types.Panel):
    bl_idname = "UtilitiesPanel"
    bl_label = "Utilities"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.export_selected_as_fbx")
        layout.prop(context.scene, "mesh_offset")
        layout.prop(context.scene, "mesh_offset_axis")


class MultiUVExport(BasePanel, bpy.types.Panel):
    bl_idname = "MultiUVExportPanel"
    bl_label = "Multi UV Export"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.multiuv_process")
        layout.operator("object.multiuv_process_and_export")


class UVTileExport(BasePanel, bpy.types.Panel):
    bl_idname = "UVTileExportPanel"
    bl_label = "UV Tile Export"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.uvtile_process")
        layout.operator("object.uvtile_process_and_export")


RegisterList = [
    ExportSelectedAsFBXOperator,
    Utilities,
    MultiUVProcess,
    MultiUVExport,
    MultiUVProcessAndExport,
    UVTileProcess,
    UVTileExport,
    UVTileProcessAndExport,
]


def register():
    for c in RegisterList:
        bpy.utils.register_class(c)


def unregister():
    for c in RegisterList:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()