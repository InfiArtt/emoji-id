# -*- coding: UTF-8 -*-
import sys
sys.dont_write_bytecode = True
import buildVars  # noqa: E402
import os  # noqa: E402

env = Environment(
    ENV=os.environ,
    tools=["default", "NVDATool"],
    toolpath=["site_scons/site_tools"],
    **{k.upper(): v for k, v in buildVars.addon_info.items()}
)

env.Default(env.Alias("addon", env.NVDAAddon("addon")))
