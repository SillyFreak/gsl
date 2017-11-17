from ruamel.yaml import YAML as _YAML
from .dot_dict import DotDict


class DotDictConstructionMixin(object):
    def construct_yaml_map(self, node):
        data = DotDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


def YAML(**kwargs):
    yaml = _YAML(**kwargs)

    class Constructor(DotDictConstructionMixin, yaml.Constructor):
        pass

    Constructor.add_constructor(
        u'tag:yaml.org,2002:map',
        Constructor.construct_yaml_map)

    yaml.Constructor = Constructor
    yaml.Representer.add_representer(DotDict, yaml.Representer.yaml_representers[dict])

    return yaml