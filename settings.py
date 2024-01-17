import json
import subprocess

settings = None
with open("settings.json","r") as reader:
    settings = json.loads(reader.read())
    #Construct a dictionary containing the settings specified in settings.json.

defaults = None
with open("defaults.json","r") as reader:
    defaults = json.loads(reader.read())

if not settings["installed"]:
    subprocess.run("pip install -r requirements.txt")


def map_name(refname:str, map=settings["name-map"])->str:
    """This function maps a backend reference name to a dispay name
    according to a name map dictionary, whose entries are formatted as:
        refname: {"default":displayname, "alt":[list of alternate names]}
    """
    return map[refname]["default"]



def capitalize_title(text:str):
    """Capitalizes the first letter of every word (delimited by spaces) in
    a string."""
    return " ".join([word.capitalize() for word in text.split(" ")])



def disambiguate(name:str, map=settings["name-map"])->str:
    """This function allows tolerance in naming convetions for column headers
    and meta tags by mapping acceptable alternate names to a specified default
    display name according to a name map dictionary, whose entries are formatted as:
        refname: {"default":displayname, "alt":[list of alternate names]}"""
    display = capitalize_title(name)
    #If the reference name isn't in the name map, just return it back since we don't
    #want to lose data.

    for refname in map:
        #Iterate over the reference names.
        if name == map[refname]["default"] or name in map[refname]["alt"]:
            display = map[refname]["default"]
            #If the input name matches a default or is in the list of alternates
            #for that reference, then we're done.
            break
    return display


def update_settings():
    """This function updates the settings object and reflects the changes in
    the source JSON file."""
    global settings

    with open("settings.json","w") as writer:
        json.dump(settings, writer, indent=4)
