# Substance Multi-UV Export
Allow for painting and baking with different UV Maps in Substance Painter. Creates duplicate meshes for every UV map and every material of the selected meshes.

# Usage guide
- Adjust the Mesh Offset to change the spacing between the processed meshes. You can use negative values to offset the meshes in the opposite direction.
- Use "Offset Axis" to change which axis the processed meshes are offset in. X is the default, but you can choose Y or Z if you need symmetry in Substance.
- Select a mesh, multiple meshes or a collection of meshes, and use "Process Meshes" to get a preview of the output. Use Ctrl + Z to undo the process.
- Once happy with the settings, use "Process Meshes and Export" to process the meshes and prompt you to export them using recommended export settings.
- Use Ctrl + Z after exporting to get rid of the processed meshes so you only ever need to worry about editing the original mesh.

# Credits <3
Jellejurre - Help with material handling
