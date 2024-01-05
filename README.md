# <img src="https://static.sidefx.com/images/apple-touch-icon.png" width="25" height="25" alt="Hbuild Logo"> Texture Stamp HDA for Houdini 20

![license](https://img.shields.io/badge/license-MIT-green) ![version](https://img.shields.io/badge/version-1.0-blue) 


### 🌠 The Texture Stamp HDA for Houdini is a simple, intuitive and user-friendly tool designed to make projecting an image onto a geometry texture (stamping) easier, in a procedural workflow.

![Stamp Interactive Demo](examples/images/stamp_tool_demo.gif)

## Key Features
- **No Setup Required**: The HDA does not need you to do anything other than tell it where the images should go, click on your mesh and start stamping!
- **Real Time Visualization**: Implemented in pure VEX, you can visualize the result of your stamping instantly.
- **Procedural By Design**: Scatter thousands of projections onto a single geometry, or precisely tune how you want your projections to behave.
- **Extendable With Custom Attributes**: Use the primitive attribute `s@stamppath` to have unlimited choice in the image you stamp, or use `v@stampcolor` to visualize different takes on your current stamped images.
- **Full OCIO Compatibility**: Your texture and stamped images are into separate colour spaces? No problem! Choose how all imports and exports behave.
- **UDIM Detection**: Any incoming geometry with extra UDIM tiles (UV ranges beyond 1) will have corresponding numbers and names read and applied, allowing you to have a streamlined and automated UDIM workflow.

## Installation
Download the HDA file and install in your `houdini20.0/otls/` folder. For detailed instructions, please refer to the [Houdini documentation](https://www.sidefx.com/docs/houdini/assets/install.html).

## Quick Start
After installing Texture-Stamp, your first step to stamping will be to connect your desired input geometry to the first input of the Texture-Stamp node. This geometry should have a UV set, so the base texture you want to stamp on can be evaluated and read correctly.

Once you have your first input geometry, it's time to start stamping! Enter the HDA's viewer state by pressing Enter on your viewport, where if your mouse is hovering over the mesh, you should see a pointer and guide to show you where the projection (and its direction) will be.

Click on the mesh and a square primitive will be created. This is a *projection mesh* - it is a UVed polygon quad that will be used in casting an orthographic projection onto the UV set of your currently selected mesh. This projection will stamp the HDA's default texture onto your mesh.

If you want to change the distance from the surface at which the projection primitive is placed, you can use `MMB` scrolling to place them further away. You can also use `Shift + LMB Drag` to change the size of the next primitive. 

You can connect your own projection primitives to the second input of the HDA, where each quad will act as its own stamping projection. Be aware that each quad will require its own UV set, and normals, as these are what determine the position of the stamp, and its direction. The projection will be exactly the same size as the quad.

## Advanced Features
Once you are up to speed with the Texture-Stamp SOP, you can use the `s@stamppath` primitive attribute (for quads connected to the second input) to specify exactly what texture you want stamped on a per-primitive level.

If you disable the default stamp texture path, you will see an error icon appear in place of any stamped projection where the `s@stamppath` attribute is not found.

You can also use the `v@stampcolor` attribute to multiply the colour of your stamp texture with the vector attribute.

If you want to change the amount of backface culling that takes place, you can change the threshold at which the projection is culled using the cull ratio ramp parameter.

![Stamp Attrib Demo](examples/images/stamp_tool_sticker.gif)

## Feedback
If you have any feedback or run into issues, please feel free to open an issue on this GitHub project. I really appreciate your support!

This tool is perfect for artists who need a quick and efficient way to add extra flavour to their textures. Add thousands of procedural stickers, effects, signs and splatters to an endless amount of geometry!