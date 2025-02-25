import re

patterns_tests = [
    (r'a[b]*', ["a", "ab", "abb", "ac", "abc"]),
    (r'a[b]{2,3}', ["abb", "abbb", "ab", "abbbb"]),
    (r'[a-z]+_[a-z]+', ["hello_world", "test_case", "Hello_World", "testCase"]),
    (r'[A-Z][a-z]+', ["Hello", "Python", "PYTHON", "Test123"]),
    (r'a.*b$', ["axb", "a123b", "ab", "abc", "aXb"]),
    (r'[ ,.]', ["Hello, world. How are you?"]),
    (r'_(.)', ["snake_case_example"]),
    (r'[A-Z][^A-Z]*', ["SplitThisString"]),
    (r'([A-Z])', ["InsertSpacesBetweenWords"]),
    (r'([A-Z])', ["CamelCaseToSnakeCase"])
]

for pattern, test_strings in patterns_tests:
    print(f"Pattern: {pattern}")
    for s in test_strings:
        if pattern == r'[ ,.]':
            print(re.sub(pattern, ":", s))
        elif pattern == r'_(.)':
            print(re.sub(pattern, lambda x: x.group(1).upper(), s))
        elif pattern == r'[A-Z][^A-Z]*':
            print(re.findall(pattern, s))
        elif pattern == r'([A-Z])' and "Spaces" in s:
            print(re.sub(pattern, r' \1', s).strip())
        elif pattern == r'([A-Z])' and "Snake" in s:
            print(re.sub(pattern, r'_\1', s).lower().lstrip('_'))
        else:
            if re.fullmatch(pattern, s):
                print(f"Match: {s}")
    print()