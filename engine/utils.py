import calendar
import json
import os
import random
import re

from django.utils import timezone

from .constants import *
from .models import *


def get_entity(question):
    entities = Entities.objects.all()

    #print("ASSSSSSSSSSSSSSSSSSSSSSSSSS", entities.values())
    list = []
    for entity in entities:
        if entity.is_this_entity(question):
            list.append(entity)
    if list:
        return list
    return UNIDENTIFIED_ENTITY

def get_intent(message):
    # print "Message:", message
    intents = Intent.objects.all().order_by('-level') # Higher the level, Higher the prirority
    list = []
    for intent in intents:
        if intent.is_this_intent(message):
            list.append(intent)
    if list:
        return list

    return UNIDENTIFIED_INTENT

def preprocess_question(question):
    words = set()
    WORD_MAP = {}
    word_mappers = WordMapper.objects.all()
    for word_mapper in word_mappers:
        for similar_word in word_mapper.get_similar_words():
            WORD_MAP[similar_word] = word_mapper.keyword

    for word in WORD_MAP:
        if word != '':
            words.add(word)
        if WORD_MAP[word] != '':
            words.add(WORD_MAP[word])
    modified_question = ''
    for word in question.split(' '):
        replacement = word
        if word in WORD_MAP:
            replacement = WORD_MAP[word]
        modified_question += replacement + ' '
    return re.sub(' +', ' ', modified_question).strip().lower()
