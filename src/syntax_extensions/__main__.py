"""
Wrapper for executing a script while using syntax extensions.

By default, doesn't activate any automic extension discorver on import/via encoding.
Pass `-e`/`-i` to achive this.

"""
from argparse import ArgumentParser

argparser = ArgumentParser(description=__doc__)

argparser.add_argument('-i', '--import', dest='activate_import', action='store_true', help="Activate the import base detection")
argparser.add_argument('-e', '--encoding', dest='activate_encoding', action='store_true', help="Activate the encoding base detection")

argparser.add_argument('-m', action='store_true', dest='module', help="script is a module that should be run")
argparser.add_argument('script', action='store', nargs='?', help="Script to execute")

argparser.add_argument('args', action='append', nargs='*', help="Arguments to pass to the script")

ns = argparser.parse_args()

if ns.activate_import:
    from syntax_extensions.activate import activate_import

    activate_import()
if ns.activate_encoding:
    from syntax_extensions.activate import activate_encoding

    activate_encoding()

# We can not rely on the fact that the script will be transformed correctly, even if both above options are on.
# We also can't easily use `runpy`, since it might compile/exec/use a loaders.get_code to achieve whatever it wants.
# These means we have to do at least some of the work of `runpy` on our own.

raise NotImplementedError('TODO')  # TODO
