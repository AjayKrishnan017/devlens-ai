from pprint import pprint

from app.services.ml_predictor import (
    MLPredictor
)


clean_code = """
def add(a, b):
    return a + b
"""


complex_code = """
def process(a, b, c, d, e, f):

    if a:
        if b:
            for item in c:
                if item:
                    if d:
                        while e:
                            if f:
                                return eval(item)

    return False
"""


predictor = MLPredictor()


print(
    "\n=== SIMPLE CODE ===\n"
)

pprint(
    predictor.predict(
        clean_code
    )
)


print(
    "\n=== COMPLEX CODE ===\n"
)

pprint(
    predictor.predict(
        complex_code
    )
)