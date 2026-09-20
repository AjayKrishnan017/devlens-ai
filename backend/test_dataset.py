from app.services.dataset_builder import DatasetBuilder


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
                                return True

    return False
"""


builder = DatasetBuilder()

builder.add_sample(
    clean_code,
    label="LOW",
    source="test_clean"
)

builder.add_sample(
    complex_code,
    label="HIGH",
    source="test_complex"
)

path = builder.save(
    "../ml/data/test_dataset.csv"
)

print(f"Dataset created: {path}")
print(f"Samples: {len(builder.rows)}")