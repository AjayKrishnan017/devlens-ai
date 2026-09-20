from pprint import pprint

from app.services.feature_extractor import FeatureExtractor


code = """
def process(user, order, payment, inventory, shipping, discount):

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


extractor = FeatureExtractor(code)

result = extractor.extract()

pprint(result)