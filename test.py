def capitalize_title(text:str):
    """Capitalizes the first letter of every word (delimited by spaces) in
    a string."""
    return " ".join([word.capitalize() for word in text.split(" ")])

print(capitalize_title("the quick brown fox _stx_"))
