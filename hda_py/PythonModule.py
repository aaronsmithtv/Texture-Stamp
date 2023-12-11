import hou


def refresh_glcache(node):
    hou.hscript("glcache -c")
    hou.hscript("texcache -c")
    