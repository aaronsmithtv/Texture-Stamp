import hou
import re


def refresh_glcache(node):
    hou.hscript("glcache -c")
    hou.hscript("texcache -c")


def assign_output_file_parms(node):
    filename = node.parm("copoutput").evalAsString()
    all_udims = node.parm("export_all_udims").evalAsInt()

    udim_pattern = re.compile(r"(<udim>|<UDIM>|<uvtile>|<UVTILE>)")

    cop_output_node = node.node("cop2net1").node("rop_comp1")

    udim_node = node.node("OUT_UDIM_ANALYSIS")
    udim_names = list(udim_node.geometry().attribValue("udim_names"))

    output_udim = node.parm("display_udim").evalAsString()

    udim_search = re.search(udim_pattern, filename)

    cop_output_parm = cop_output_node.parm("copoutput")

    if udim_search:
        new_name_single = re.sub(udim_pattern, output_udim, filename)
        cop_output_parm.set(new_name_single)

        if output_udim in udim_names:
            udim_names.remove(output_udim)
    else:
        cop_output_parm.set(filename)

    cop_output_node.parm("execute").pressButton()

    if len(udim_names) > 0 and all_udims and udim_search:
        with hou.InterruptableOperation("Processing UDIMs", open_interrupt_dialog=True) as operation:
            for i, udim_name in enumerate(udim_names):
                percent = float(i) / float(len(udim_names))
                operation.updateProgress(percent)

                node.parm("display_udim").set(udim_name)

                new_name_multi = re.sub(udim_pattern, udim_name, filename)
                cop_output_parm.set(new_name_multi)

                cop_output_node.parm("execute").pressButton()

    node.parm("display_udim").set(output_udim)
    refresh_glcache(node)
