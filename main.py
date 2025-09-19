import requests as r
import json

class definition:
    def __init__(self, name, synonyms, antonyms, example):
        self.name = name
        self.synonyms = synonyms
        self.antonyms = antonyms
        self.example = example
        
    def say_hey(self):
        print(self.name)
        if (self.synonyms != []):
            print("---Synonyms:")
            for i in self.synonyms:
                if (i != ''):
                    print("----", end='')
                    print(i)
        if (self.antonyms != []):
            print("---Antonyms:")
            for i in self.antonyms:
                print("----", end='')
                print(i)
        if (self.example != ''):
            print("---Exapmple: "+"\n----"+self.example)

class part_of_speech:
    def __init__(self, name, definitions):
        self.name = name
        self.definitions = definitions
    def say_hey(self):
        print(self.name)
        for i in self.definitions:
            print("--", end='')
            i.say_hey()

class card:
    def __init__(self, word,phonetic,parts_of_speech):
        self.word = word
        self.phonetic = phonetic
        self.parts_of_speech = parts_of_speech
        
    def print_card(self):
        print(self.word + "\n" + self.phonetic)
        for i in self.parts_of_speech:
            print("-", end='')
            i.say_hey()

    def create_sides(self, config):
        front_side = ''
        back_side = ''
        front_config = config[:config.find("|")]
        back_config = config[config.find("|")+1:]
        
def get_val(inp):
    val = inp[inp.find(':')+2:-1]
    return val

def is_in_arr(inp_str, arr):
    for i in arr:
        if (inp_str in i):
            return 1
    return 0

def find_in_arr(inp_str, arr):
    out = 0
    for i in arr:
        if (inp_str in i):
            return out
        out += 1

    return -1

def parse_word(hello):
    
    out = card("", "", [])
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{hello}"
    json_string = r.get(url).text

    l = json_string.split("{")
    
    arr = []
    for i in l:
        for j in i.split(','):
            arr.append(j)

    c = 0
    while c < len(arr):
        arr[c] = arr[c].replace("}", "")
        i = arr[c]
        if (":" not in i):
            arr[c-1] = arr[c-1] + i
            arr.pop(c)
            c -= 1
        c += 1

    parts_of_speech = []
    if (is_in_arr("Sorry pal we couldn't find definitions for the word you were looking for.", arr) == 1):
        return 0
    for i in arr:
        if ( 'phonetic"' in i ):
            out.phonetic = get_val(i)
        if ( "word" in i ):
            out.word = get_val(i)
        #print(i)

    while is_in_arr("partOfSpeech", arr):
        tmp = part_of_speech("", [])
        ind = find_in_arr("partOfSpeech", arr)
        tmp.name = get_val(arr[ind])
        arr = arr[ind+1:]
        defs = []
        while (find_in_arr('definition"', arr) < find_in_arr("partOfSpeech", arr)) or (is_in_arr("partOfSpeech", arr) == 0 and find_in_arr('definition"', arr) < len(arr)-1):
            tmp_def = definition("", [], [], "")
            ind_d = find_in_arr('definition"', arr)
            if ind_d == -1:
                break
            tmp_def.name = get_val(arr[ind_d])

            if ("synonyms" in arr[ind_d+1]):
                tmp_def.synonyms = get_val(arr[ind_d+1]).replace('""','"').split('"')[1:-1]

            if ("antonyms" in arr[ind_d+2]):
                tmp_def.antonyms = get_val(arr[ind_d+2]).replace('""','"').split('"')[1:-1]

            if ("example" in arr[ind_d+3]):
                tmp_def.example = get_val(arr[ind_d+3])
            
            
            defs.append(tmp_def)
            arr = arr[ind_d+1:]
        tmp.definitions = defs
        parts_of_speech.append(tmp)
    out.parts_of_speech = parts_of_speech
    print("\n\n")
    out.print_card()
    return out
with open("inp.txt", "r") as f:
    arr = f.readlines()
    f.close()
deck = []
correct = 0
not_found = []
for i in arr:
    card_ = parse_word(i[:-1])
    if (card_ == 0):
        not_found.append(i)
        continue
    correct += 1
    deck.append(card_)

print(f"\nAll requests: {len(arr)}\nFound: {correct}\nNot found is:")
for i in not_found:
    print(i)
