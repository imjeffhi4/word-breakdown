from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from fastapi import FastAPI
import re
import json
from pydantic import BaseModel 
from typing import Optional
import torch

app = FastAPI()

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
morph_path = './Model'
morph_tokenizer = GPT2Tokenizer.from_pretrained(morph_path)
special_tokens = {'bos_token': '<|startoftext|>', 'pad_token': '<PAD>', 'additional_special_tokens':['<DEF>', '<SYLLABLES>', '<NULL>', '<ETY>', '<MORPH>']}
morph_tokenizer.add_special_tokens(special_tokens)
morph_model = GPTNeoForCausalLM.from_pretrained(morph_path).to(device)

class UserInput(BaseModel):
    word: str
    definition: Optional[str] = None

# returning WikiMorph output
@app.post('/')
async def main(x: UserInput):
    return get_morpheme_output(x.word, x.definition)

def get_etymology(ety_txt):
    """Parses text to return a list of dict containing the etymology compound and definitions"""
    etys = re.findall('<ETY>.+?(?=<ETY>|$)', ety_txt)
    for ety in etys:
        compound = re.findall("<ETY>(.+?)(?=<DEF>|$)", ety)[0].strip()
        if "<NULL>" not in compound:
            ety_dict = {
                "Etymology Compound": re.findall("<ETY>(.+?)(?=<DEF>)", ety)[0].strip(),
                "Compound Meaning": re.findall("<DEF>(.+)", ety)[0].strip()
            }
            yield ety_dict
        else:
            yield {"Etymology Compound": None, "Compound Meaning": None}


def parse_morphemes(morph_txt):
    """Parses text to return a list of affixes and a definition for each affix"""
    morphs = re.findall('<MORPH>.+?(?=<MORPH>|$)', morph_txt)
    for morph in morphs:
        yield {
            "Morpheme": re.findall("<MORPH>(.+?)(?=<DEF>)", morph)[0].strip(),
            "Definition": re.findall("<DEF>(.+?)(?=<ETY>)", morph)[0].strip(),
            "Etymology Compounds": list(get_etymology(re.findall("(<ETY>.+?)$", morph)[0].strip()))
        }


def to_dict(generated_txt):
    """Returns a dictionary containing desired items"""
    return {
        "Word": re.findall('<\|startoftext\|> (.+?)(?= \w )', generated_txt)[0].strip().replace(' ', ''),
        "Definition": re.findall("<DEF>(.+?)(?=<SYLLABLES>)", generated_txt)[0].strip(),
        "Syllables": re.findall("<SYLLABLES> (.+?)(?=<MORPH>)", generated_txt)[0].strip().split(),
        "Morphemes": list(parse_morphemes(re.findall("(<MORPH>.+?)(?=<\|endoftext\|>)", generated_txt)[0].strip()))
    }


def get_morpheme_output(word, definition):
    """Calls the GPT-based model to generated morphemes"""
    split_word = ' '.join(word)
    if definition:
        word_def = f'<|startoftext|> {word} {split_word} <DEF> {definition} <SYLLABLES>'
    else:
        word_def =  f'<|startoftext|> {word} {split_word} <DEF> '
    tokenized_string = morph_tokenizer.encode(word_def, return_tensors='pt').to(device)
    output = morph_model.generate(tokenized_string, max_length=400)
    generated_txt = morph_tokenizer.decode(output[0])
    return to_dict(generated_txt)
