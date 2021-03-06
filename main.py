#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### JAnkiAutogen: Automatic Japanese cloze generator
# Input Japanese text and get back a massive set of cloze deletion problems
# Eventually: Get back an anki deck you can import

# TODO:
#   - Make it work for a large document (e.g. wikipedia article or https://semver.org/lang/ja/)
#       - Auto split into paragraphs (would anyone paste a whole document like this?)
#   - Put proper instructions in the docs

# METHOD:
# Deck GUIDs from random.randrange(1 << 30, 1 << 31)
# generate cloze from text e.g.
# APIの変更に互換性のない場合はメジャーバージョンを
# =>
# API の 変更 に 互換性 の ない 場合 は メジャー バージョン を
# APIの{cloze::変更}{furigana::へんこう}に互換性のない場合はメジャーバージョンを
# + for all other non-particle words initially?
# Don't repeat for multiple instances of same word
# Add optional furigana
import MeCab
import genanki
import jaconv
import re
import random
import sys

def create_note(cloze, sentence, model):
    # TODO: sentence -> paragraph / wholetext
    note = genanki.Note(
        model=model,
        fields=[cloze, sentence],
        sort_field = '',
        tags = None,
        guid = random.randrange(1 << 30, 1 << 31),
        )
    return note

def create_deck(clozes, sentence, furigana = False, deckfile = 'JAnkiAutogen_Output.apkg', setname = "Default Deck"):
    # Create anki deck from words / text block
    # TODO: Can we retrieve / load an existing deck / deck ID?
            # Need to pass sentence
    # Access / generate deck
    notecount = 0 # How many notes are produced?
    newid = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(newid, setname)
    # Set up card model
    model = genanki.Model(
        1607392319,
        'Word',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<span style="font-size:32px">{{furigana:Question}}</span>',
                'afmt': '<span style="font-size:32px">{{furigana:Answer}}</span>'
            }]
        
    )
    # Generate notes (flashcards)
    if furigana:
        for i in range(len(clozes)):
            clozenote = create_note(clozes[i], sentences[i], model)
            deck.add_note(clozenote)
            notecount += 1
    else:
        for cloze in clozes:
            clozenote = create_note(cloze, sentence, model)
            deck.add_note(clozenote)
            notecount += 1
    genanki.Package(deck).write_to_file(deckfile)
    print("Deck built: "+str(notecount)+" notes.")

def load_text(textfile):
    with open(textfile, "r") as file:
        text = file.read()
    t = MeCab.Tagger("-Owakati")
    s = t.parse(text)
    wordlist = s.split(" ")
    wordlist.remove("\n")
    # TODO: Remove punctuation e.g. "。"
    return text, wordlist

def make_clozes(sentence, wordlist):
    clozes = []
    for word in wordlist:
        cloze = re.sub(word, '「...」', sentence)
        clozes.append(cloze)
    return clozes

def furiganify(sentence, wordlist):
    # TODO Only Kanji
    # --- Find words with Kanji
    t = MeCab.Tagger('-Oyomi')
    sentences = []
    nonkanji = []
    for word in wordlist:
        if re.findall(r'[\u4e00-\u9fea]+',word):
            w = t.parse(word)
            w = re.sub(r'\n', '', w)
            w = jaconv.kata2hira(w)
            furi_sentence = re.sub(word, " "+word+'['+w+']', sentence)
            sentences.append(furi_sentence)
        else:
            nonkanji.append(word)
    for word in nonkanji:
        wordlist.remove(word)
    clozes = make_clozes(sentence, wordlist)
    return clozes, sentences

if __name__ == "__main__":

    # --- Get text from file
    # TODO Choose a text file when you run it:
    #   $python main.py filename.txt
    #   Eventually: $JAnkiAutogen infile.txt outfile.apkg 'Deck Title'
    sentence, wordlist = load_text('input.txt') # os.path | argument in terminal | look for default filename?
    #sentence, wordlist = load_text(" ".join(sys.argv))
    # --- Turn text into clozes for printing to screen
    # put html <br /> line breaks for Anki
    sentence = sentence.replace('\n', '<br />')
    #clozes = make_clozes(sentence, wordlist)

    clozes, sentences = furiganify(sentence, wordlist)
    for cloze in clozes:
        print(cloze)
    # --- Create anki deck from cloze deletions
    # no furigana
    #create_deck(clozes, sentence, False, 'TestDeck.apkg', 'JAA Test Deck')
    # with furigana
    create_deck(clozes, None, True, 'TestDeck.apkg', 'JAA Test Deck')
