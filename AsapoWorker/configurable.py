import attr

CONFIGURABLE_CONFIG_ENTRY = "__configurable_config_entry"


@attr.s
class _ConfigEntry():
    description = attr.ib(type=str)
    builder = attr.ib()
    short_option = attr.ib(type=str, default=None)
    proxy = attr.ib(type=type, default=None)
    flatten = attr.ib(type=bool, default=False)


def config_entries(type):
    return filter(lambda field: field.init, attr.fields(type))


def flattened_config_entries(type):
    flattened_entries = []

    for field in config_entries(type):
        config_entry = field.metadata[CONFIGURABLE_CONFIG_ENTRY]

        if config_entry.proxy is not None:
            sub_configurable = config_entry.proxy
        elif attr.has(field.type):
            sub_configurable = field.type
        else:
            sub_configurable = None

        if config_entry.flatten:
            if sub_configurable is None:
                raise ValueError(
                    "Attribute '{}' cannot be flattened".format(field.name))
            for subfield in flattened_config_entries(sub_configurable):
                if subfield not in flattened_entries:
                    flattened_entries.append(subfield)
        else:
            if field not in flattened_entries:
                flattened_entries.append(field)

    return flattened_entries


def get_config_entry_option(attribute, name):
    if hasattr(attribute.metadata[CONFIGURABLE_CONFIG_ENTRY], name):
        value = getattr(attribute.metadata[CONFIGURABLE_CONFIG_ENTRY], name)
    else:
        value = getattr(attribute, name)
    return value


def check_type(obj):
    for attribute in attr.fields(type(obj)):
        expected_type = get_config_entry_option(attribute, 'type')
        variable = getattr(obj, attribute.name)
        if not isinstance(variable, expected_type):
            raise TypeError("Variable '{}' has wrong type '{}', expected '{}'".format(attribute.name,
                                                                                      type(variable),
                                                                                      expected_type))


def Configurable(maybe_cls=None, *args, **kwargs):
    def attrs_wrapper(cls):
        cls = attr.s(*args, **kwargs)(cls)
        doc = ""
        for field in config_entries(cls):
            if field.type is None:
                typename = ""
            else:
                typename = field.type.__name__
            doc += "\n{name}: {type}\n   {desc}".format(
                name=field.name, type=typename,
                desc=field.metadata[CONFIGURABLE_CONFIG_ENTRY].description)
        if cls.__doc__:
            if cls.__doc__.count("\n") > 3:
                try:
                    new_doc = cls.__doc__.format(parameter_description=doc[1:])
                    cls.__doc__ = new_doc
                except KeyError:
                    pass
            else:
                new_doc = cls.__doc__ + "\n" + doc
                cls.__doc__ = new_doc

        else:
            cls.__doc__ = cls.__name__ + "\n" + doc
        return cls

    if maybe_cls is None:
        return attrs_wrapper
    else:
        return attrs_wrapper(maybe_cls)


def Config(
        description, type=None, default=attr.NOTHING, factory=None,
        short_option=None, arguments=None, builder=None, flatten=False,
        metadata=None, **kwargs):
    """A parameter of a Configurable

    Parameters
    ----------
    description: str
        A description of the parameter
    type: type, optional
        The type of the parameter
    default: optional
        A default value. Must be of the type specified by 'type'
    factory: callable, optional
        Will be called with zero arguments to create a default value
    short_option: str, optional
        An additional command line option for this parameter
    arguments: dict of str to Config, optional
        If type is a complex type and no Configurable, the arguments keyword
        can be used to enable auto-configuration for this type without the need
        to create a wrapper class, etc.
        If type is a Configurable, its auto-configuration will be overwritten
    builder: callable, optional
        Will be called with parameters given by arguments to create an instance
        from configuration. If None (the default), type will be called instead.
        If type is a Configurable, arguments may be omitted.
    flatten: boolean, optional
        If true, the parameters of this complex type attribute will part of the
        class namespace. If true for two or more attributes that have
        parameters with the same name, the affected parameters must be
        exactly identical
    For other parameters, see 'attr.ib'
    """
    if metadata is None:
        metadata = {}
    if factory is not None:
        default = attr.Factory(factory)
    if builder is None:
        builder = type
    if arguments is not None:
        if builder is None:
            raise ValueError("'arguments' given but no 'type' or 'builder'")
        proxy = attr.make_class(
            builder.__name__ + "_ConfigProxy", arguments)
    else:
        proxy = None
    config_entry = _ConfigEntry(
        description=description, builder=builder, short_option=short_option,
        proxy=proxy, flatten=flatten)
    metadata[CONFIGURABLE_CONFIG_ENTRY] = config_entry
    return attr.ib(type=type, default=default, metadata=metadata, **kwargs)
