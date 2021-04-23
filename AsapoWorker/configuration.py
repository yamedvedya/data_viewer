import attr
from AsapoWorker.configurable import (
    config_entries, flattened_config_entries, CONFIGURABLE_CONFIG_ENTRY, get_config_entry_option)
import argparse


def create_config_from_configurable_class(configurable_class):
    config = {}
    for field in config_entries(configurable_class):
        config[field.name] = create_config_for_attribute(field)
    return config


def create_config_for_attribute(attribute):
    config_entry = attribute.metadata[CONFIGURABLE_CONFIG_ENTRY]
    if config_entry.proxy is not None:
        return create_config_from_configurable_class(config_entry.proxy)
    elif attr.has(attribute.type):
        return create_config_from_configurable_class(attribute.type)
    else:
        return attribute.default


create_config = create_config_from_configurable_class


def create_yaml_from_configurable_class(
        configurable_class, indent=-1):
    if indent == -1:
        yaml = configurable_class.__name__ + ":\n"
        indent = 0
    else:
        yaml = ""
    for field in flattened_config_entries(configurable_class):
        yaml += create_yaml_for_attribute(field, indent=indent)
    return yaml


def create_yaml_for_attribute(attribute, indent):
    config_entry = attribute.metadata[CONFIGURABLE_CONFIG_ENTRY]
    assert not config_entry.flatten

    yaml = ""
    indent += 1
    yaml += "{indent}# {description}\n".format(
        indent=" "*4*indent,
        description=config_entry.description)

    if config_entry.proxy is not None:
        sub_configurable = config_entry.proxy
    elif attr.has(attribute.type):
        sub_configurable = attribute.type
    else:
        sub_configurable = None

    if sub_configurable:
        yaml += "{indent}{name}:\n".format(
            indent=" "*4*indent, name=attribute.name)
        return yaml + create_yaml_from_configurable_class(
            sub_configurable, indent)
    else:
        yaml += "{indent}{comment}{name}:".format(
            indent=" "*4*indent, name=attribute.name,
            comment="" if attribute.default is attr.NOTHING else "# ")
        if attribute.default is attr.NOTHING:
            ret = yaml + "  # TODO: enter value"
            if attribute.type:
                ret += " of type " + attribute.type.__name__
            return ret + "\n"
        elif isinstance(attribute.default, attr.Factory):
            return yaml + "\n"
        else:
            return yaml + " " + repr(attribute.default) + "\n"


def create_cli_parser_from_configurable_class(
        configurable_class, parser=None, prefix="", short_prefix=None):
    if not parser:
        parser = argparse.ArgumentParser(
            prog="Application",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    if not prefix:
        prefix = configurable_class.__name__ + "."

    if short_prefix is None:
        short_prefix = prefix

    for field in flattened_config_entries(configurable_class):
        create_cli_parser_for_attribute(field, parser, prefix, short_prefix)
    return parser


def create_cli_parser_for_attribute(attribute, parser, prefix, short_prefix):
    config_entry = attribute.metadata[CONFIGURABLE_CONFIG_ENTRY]
    assert not config_entry.flatten

    if config_entry.proxy is not None:
        sub_configurable = config_entry.proxy
    elif attr.has(attribute.type):
        sub_configurable = attribute.type
    else:
        sub_configurable = None

    if sub_configurable is not None:
        if config_entry.short_option is not None:
            if config_entry.short_option:
                short_prefix += "{name}.".format(
                    name=config_entry.short_option)
        else:
            short_prefix += "{name}.".format(name=attribute.name)
        prefix += "{name}.".format(name=attribute.name)
        create_cli_parser_from_configurable_class(
            sub_configurable, parser, prefix,
            short_prefix)
    else:
        if config_entry.short_option:
            if short_prefix:
                option = ["--" + short_prefix
                          + config_entry.short_option]
            else:
                option = ["-" + config_entry.short_option]
        else:
            option = []
        option.append("--{prefix}{name}".format(
            prefix=prefix, name=attribute.name))

        if attribute.type:
            metavar = attribute.type.__name__.upper()
        else:
            metavar = "ARG"

        description = config_entry.description

        if attribute.default is attr.NOTHING:
            default = None
            required = True
        elif isinstance(attribute.default, attr.Factory):
            default = argparse.SUPPRESS
            required = False
        else:
            default = argparse.SUPPRESS
            description += " (default: {})".format(attribute.default)
            required = False

        if attribute.converter:
            typ = attribute.converter
        else:
            typ = attribute.type

        parser.add_argument(
            *option,
            type=typ, metavar=metavar, required=required,
            default=default, help=description)


def create_instance_from_configurable(
        type, options, kwargs=None, builder=None):
    if kwargs is None:
        kwargs = {}
    if builder is None:
        builder = type
    for field in config_entries(type):
        create_instance_from_attribute(field, options, kwargs)
    return builder(**kwargs)


def create_instance_from_attribute(attribute, options, kwargs):
    if attribute.name in kwargs:
        return
    config_entry = attribute.metadata[CONFIGURABLE_CONFIG_ENTRY]
    if not config_entry.flatten:
        options = options.get(attribute.name, {})
    if config_entry.proxy is not None:
        proxy_instance = create_instance_from_configurable(
            config_entry.proxy, options)
        kwargs[attribute.name] = config_entry.builder(
            **attr.asdict(proxy_instance))
    elif attr.has(attribute.type):
        kwargs[attribute.name] = create_instance_from_configurable(
            attribute.type, options, builder=config_entry.builder)
    else:
        if options:
            kwargs[attribute.name] = options


def parsed_args_to_dict(parsed):
    parsed = vars(parsed)
    options = {}
    for key, value in parsed.items():
        keys = key.split(".")
        d = options
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
    return options
