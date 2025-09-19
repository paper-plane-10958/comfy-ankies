import requests as r
import json
import sys
from deep_translator import GoogleTranslator
from datetime import datetime
from random import randint

def trans_to_rus(inp):
    translated = str(GoogleTranslator(source='auto', target='ru').translate(inp))
    return translated

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

def del_duplicates(arr):
    out = []
    for i in arr:
        if i in out:
            continue
        out.append(i)
    return out


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

    def create_side_from_config(self, config):
        side = ''
        for i in config:
            if 'word' in i:
                if '-ru' in i:
                    side += trans_to_rus(self.word)
                    side += "<br>"
                    continue
                side += self.word
                side += "<br>"
            if i == 'phonetic':
                side += self.phonetic
                side += "<br>"
            if 'synonyms' in i:
                side += "<br>Synonyms:<br>"
                for j in self.parts_of_speech:
                    tmp = []
                    for k in j.definitions:
                        tmp.extend(k.synonyms)
                    num = 3
                    if (len(tmp) < 3):
                        num = len(tmp)
                    if (tmp == []):
                        continue
                    side += j.name + ': '
                    for m in range(num):
                        if ("-ru" in i):
                            if (j.name == "verb"):
                                side += trans_to_rus("i want to " + tmp[m])[7:]
                            elif (j.name == "noun"):
                                side += trans_to_rus("big " + tmp[m])[8:]
                            elif (j.name == "adjective"):
                                side += trans_to_rus(tmp[m] + " spider")[:-5]
                            else:
                                side += trans_to_rus(tmp[m])

                        else:
                            side += tmp[m]
                        if (m != num - 1):
                            side += ", "
                    side += "<br>"
            if ('definitions' in i):
                side += "<br>Definitions:<br>"
                for j in self.parts_of_speech:
                    k = j.definitions[0]
                    if ("-ru" in i):
                        side += j.name + ": " + trans_to_rus(k.name) + "<br>"
                    else:
                        side += j.name + ": " + k.name + "<br>"
        return side



    def create_sides(self, front_config, back_config, file_name):
        front_config = del_duplicates(front_config.split())
        back_config = del_duplicates(back_config.split())
        front_side = self.create_side_from_config(front_config)
        back_side = self.create_side_from_config(back_config)


        if (front_side[-4:] == "<br>"):
            front_side = front_side[:-4]
        if (back_side[-4:] == "<br>"):
            back_side = back_side[:-4]
        with open(file_name, "a", encoding = "UTF-8") as f:
            f.write(front_side.replace(";", ",")+";"+back_side.replace(";", ",")+"\n")
            f.close
        print("Front side: "+front_side +"\nBack side: "+ back_side)

        
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
            arr[c-1] = (arr[c-1] + i).replace(";", ".")
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
    if out.phonetic == '':
        out.phonetic = '[sry, no bekmek]'
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
    return out
def main():
    # getting config

    argv_ = sys.argv
    file_config = 'example_input.txt'
    file_name = ''
    front_config = ''
    back_config = ''
    for i in range(len(argv_)):
        tmp = argv_[i]
        if (tmp == "-i"):
            file_config = argv_[i+1]
            i += 1
        if (tmp == "-b"):
            back_config = argv_[i+1]
            i += 1
        if (tmp == "-f"):
            front_config = argv_[i+1]
            i += 1
        if (tmp == "-o"):
            file_name = argv_[i+1]
            i += 1
    # reading words
    if file_config == '':
        print("No such file err")
        return -1
    with open(file_config, "r") as f:
        arr = f.readlines()
        f.close()
    # parse API and setting summary

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
    print(f"\nAll requests: {len(arr)}\nFound: {correct}")
    if (not_found != []):
        print("Not found is:")
        for i in not_found:
            print(i)

    # creating out file

    if file_name == '':
        current_datetime = datetime.now()
        current_time_str = current_datetime.strftime("%H-%M")
        file_name = "./outs/"+current_time_str + "session-" +str(randint(0,100)) +".txt"
    with open(file_name, "w", encoding = "UTF-8") as f:
        f.write("")
        f.close

    for i in deck:
        i.create_sides(front_config, back_config, file_name)

if __name__ == "__main__":
    main()
