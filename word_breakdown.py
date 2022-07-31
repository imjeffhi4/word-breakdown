from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from fastapi import FastAPI
from breakdown_pipeline import WordBreakdownPipeline
from pydantic import BaseModel 
from typing import Optional
import torch

app = FastAPI()

device = 0 if torch.cuda.is_available() else -1
morph_path = './Model'
morph_tokenizer = AutoTokenizer.from_pretrained(morph_path)
morph_model = AutoModelForCausalLM.from_pretrained(morph_path).to(device)
breakdown_pipe = pipeline('text-generation', model=morph_model, tokenizer=morph_tokenizer, pipeline_class=WordBreakdownPipeline, device=0)

class UserInput(BaseModel):
    word: str
    definition: Optional[str] = None

# returning WikiMorph output
@app.post('/')
async def main(x: UserInput):
    return get_morpheme_output(x.word, x.definition)

def get_morpheme_output(word: str, definition: str = ""):
    """Calls the GPT-based model to generated morphemes"""
    input_dict = {'word': word, 'definition': definition}
    print(input_dict)
    output = breakdown_pipe(input_dict, max_length =512, early_stopping=True, do_sample=False)
    return output[0]['generated_breakdown']
