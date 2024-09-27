import re

pattern = r"\d+"
text = "Phone no is 78765656 with 86756"

matches = re.findall(pattern, text)
print(matches)