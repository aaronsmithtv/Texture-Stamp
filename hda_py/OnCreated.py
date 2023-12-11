import hou

node = kwargs["node"]

# Set Colour
pink = hou.Color((0.8, 0.65, 0.85))
node.setColor(pink)

# node.parm("output_file").pressButton()

# Add a comment to the node
node.setComment("aaronsmith.tv")

# Enable the comment in the network editor
node.setGenericFlag(hou.nodeFlag.DisplayComment, True)
