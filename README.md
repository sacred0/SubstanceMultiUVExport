# Substance Multi-UV Export
Creates duplicate meshes for every UV map of the selected meshes to allow for painting with different UV maps in Substance Painter.
Supports unlimited UV maps, materials, and meshes.

![SMUVE_b1](https://github.com/sacred0/SubstanceMultiUVExport/assets/105738663/c01a68d7-d48a-4aac-b80b-20bbbfbc248b)
![SMUVE_b2](https://github.com/sacred0/SubstanceMultiUVExport/assets/105738663/12517bd4-a645-4f8d-8bf9-557bed0f05ee)
![SMUVE_s1](https://github.com/sacred0/SubstanceMultiUVExport/assets/105738663/b6dbff18-7e4b-404e-8b54-728e0e6c293e)



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
