# Substance Multi-UV Export
Creates duplicate meshes for every UV map and every material of the selected meshes to allow for painting with different UV Maps in Substance Painter.

# Installation
- Download latest .py script from Releases
- In Blender, go to Edit > Preferences > Add-ons, click Install, and locate the file
- Enable the add-on by clicking the checkbox. It will show up as a tab in the viewport sidebar (press N in viewport)

# Usage guide
- Adjust the Mesh Offset to change the spacing between the processed meshes. You can use negative values to offset the meshes in the opposite direction.
- Use "Offset Axis" to change which axis the processed meshes are offset in. X is the default, but you can choose Y or Z if you need symmetry in Substance.
- Select a mesh, multiple meshes or a collection of meshes, and use "Process Meshes" to get a preview of the output. Use Ctrl + Z to undo the processing.
- Once happy with the settings, use "Process Meshes and Export" to process the meshes and prompt you to export them using recommended export settings.
- After exporting, use Ctrl + Z to remove the processed meshes. You only ever need to worry about the one original mesh, since you can re-process anytime.

# Credits <3
Jellejurre - Help with material handling
