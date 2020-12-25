_already_activated = {}


def activate_encoding(tar_names=('syntax-extensions',)):
    from encodings import normalize_encoding
    from codecs import register
    from syntax_extensions.activate.encoding import codec_info

    names = _already_activated.setdefault('encoding', set())

    if names:
        names.update(normalize_encoding(n) for n in tar_names)
        return
    else:
        names.update(normalize_encoding(n) for n in tar_names)

        def finder(n: str):
            if normalize_encoding(n) in names:
                return codec_info
            else:
                return None

        register(finder)


def activate_import(*args, **kwargs):
    from syntax_extensions.activate.import_hooks import activate_import
    activate_import(*args, **kwargs)
