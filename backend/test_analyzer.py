from app.analyzers.syntax_analyzer import CodeAnalyzer


sample_code = """
import os
import json


class UserManager:

    def get_users(self):

        users = []

        for i in range(10):

            if i % 2 == 0:
                users.append(i)

        return users


def calculate(a, b):

    try:
        return a / b

    except ZeroDivisionError:
        return 0
"""


analyzer = CodeAnalyzer(sample_code)

result = analyzer.analyze_structure()

print(result)