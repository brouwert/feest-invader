from logging import DEBUG
import logging
import time

from generators import SineWave, Toggle, Range
from model import EffectDefinition, BooleanParameter

logging.basicConfig(level=DEBUG)

class VliegEffect:
    @classmethod
    def definition(cls):
        return EffectDefinition('vlieg', ['wings'], [
            BooleanParameter('left'),
            BooleanParameter('right')])

    def __init__(self, controller, parameters, effectenbak):

        self.controller = controller
        self._left = parameters.get('left')
        self._right = parameters.get('right')

        self._generator = Range(lower=0, upper=3)

    def ticks_per_iteration(self):
        return self._generator.ticks()

    def tick(self):
        i = self._generator.next()

        if self._left:
            self.controller.wings.left(False)
            self.controller.wings.left_index(i, True)

        if self._right:
            self.controller.wings.right(False)
            self.controller.wings.right_index(i, True)

        time.sleep(.2)

    def finalize(self):
        if self._left:
            self.controller.wings.left(False)
        if self._right:
            self.controller.wings.right(False)


effect = VliegEffect
