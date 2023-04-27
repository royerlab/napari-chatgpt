import re


def camel_case_to_lower_case(string):
    # Use regular expression to find all uppercase letters that come after a lowercase letter
    # or a digit, and replace them with the same letters but with a preceding space and in lower case.
    # For example, "myCamelCaseString" becomes "my camel case string".
    result = re.sub(r'(?<=[a-z0-9])[A-Z]',
                    lambda match: f' {match.group(0).lower()}', string)

    # Ensure everything is lower case, including first letter:
    result = result.lower()

    return result
