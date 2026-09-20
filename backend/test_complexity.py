from pprint import pprint

from app.analyzers.complexity_analyzer import ComplexityAnalyzer


code = """
def process_order(user, order, payment, inventory, shipping, discount):

    if user:

        if order:

            for item in order:

                if item:

                    if inventory:

                        while payment:

                            if shipping:
                                return True

    return False
"""


analyzer = ComplexityAnalyzer(code)

report = analyzer.analyze()

pprint(report)