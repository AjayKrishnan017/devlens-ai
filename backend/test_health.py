from pprint import pprint

from app.services.health_engine import HealthEngine


code = """
from math import *


class Calculator:

    def calculate(self, values=[]):

        # TODO: improve validation

        for value in values:

            if value:

                try:
                    result = eval(value)

                except:
                    pass

        return True
"""


engine = HealthEngine(code)

report = engine.analyze()

pprint(report)