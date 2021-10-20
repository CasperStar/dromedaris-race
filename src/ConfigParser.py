import yaml

import time # TODO: Remove Debug


class Test:
    def __init__(self, a, b, c):
        self._a, self._b, self._c, = a, b, c

    def get_a(self) -> int:
        return self._a

class MPC:
    def __init__(self, z):
        self._z = z

    def get_z(self) -> int:
        return self._z

class ConfigParser:

    def __init__(self):
        pass

    def test_constructor(self, loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> Test:
        return Test(**loader.construct_mapping(node))

    def mpc_constructor(self, loader: yaml.SafeLoader, node: yaml.nodes.MappingNode) -> MPC:
        return MPC(**loader.construct_mapping(node))

    def get_loader(self):
        loader = yaml.SafeLoader
        loader.add_constructor("!Test", self.test_constructor)
        #loader.add_constructor("!MPC", self.mpc_constructor)
        return loader

    def LoadConfig(self, config_path):
        try:
            objects = yaml.load(open(config_path, "r"), Loader=self.get_loader())
        except yaml.YAMLError as exception:
            print(exception)
            time.sleep(5)
        for obj in objects:
            print (obj.get_a())

        pass

    def LoadConfig2(self, config_path):
        with open(config_path) as f:
            # use safe_load instead load
            dataMap = yaml.safe_load(f)

        print(dataMap)

        extender_mapping = dataMap.get("ExtenderMapping")
        print(extender_mapping)
