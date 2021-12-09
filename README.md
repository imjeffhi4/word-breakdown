# Word Breakdown

A fine-tuned version of [GPT Neo](https://huggingface.co/EleutherAI/gpt-neo-125M) (small, 125M parameters) trained on the [WikiMorph dataset](https://zenodo.org/record/5172857) to break down words into different types of components. These components include the following:

1. **Morphemes:** Smallest unit within a word that contains meaning. (e.g., if the word is ultraviolet, it returns "[ultra-, violet]". ) 
2. **Syllables:** Syllables of the given word
3. **Etymology Compounds:** morphemes from root languages (mostly latin/greek)
4. **Definitions:** Defines each morpheme and etymology compound. 

# How to Run

Building the docker image:

```docker
docker build --no-cache -t word_breakdown .
```

You can then run the API with the following:

```docker
docker run -p 8000:8000 word_breakdown
```

# Using the API

To use the API, make a POST request to the URL "[http://127.0.0.1:8000/](http://127.0.0.1:8000/)". It accepts the word and optionally a definition for that word. If the user gives the model an initial definition, the model will attempt to relate subsequent morpheme definitions to it. If an initial definition is not given for the initial word, it'll autoregressively try to generate one. (quality will vary). An example request may look like the following:

```python
word = "ultraviolet"
definition = "of electromagnetic radiation beyond (higher in frequency than) light visible to the human eye; radiation with wavelengths from 380 nanometre - 10 nanometre"
items= {"word": word, 'definition': definition} # definition is optional
x = requests.post('http://127.0.0.1:8000/', json=items)
output = json.loads(x.content)
```

# Results

For the word "ultraviolet" without an initial definition:

```json
{
  "Word": "ultraviolet",
  "Definition": "Extremely visible.",
  "Syllables": "ul tra vi o let",
  "Morpheme": [
    {
      "Morpheme": "ultra-",
      "Definition": "Excessively, to an extreme, as in ultramicroscopic, ultra-careful.",
      "Etymology Compounds": [
        {
          "Etymology Compound": "uls",
          "Compound Meaning": "beyond"
        },
        {
          "Etymology Compound": "-ter",
          "Compound Meaning": "-ly; used to form adverbs from adjectives."
        },
        {
          "Etymology Compound": "-a",
          "Compound Meaning": "adverb"
        }
      ]
    },
    {
      "Morpheme": "violet",
      "Definition": "Having a bluish-purple colour.",
      "Etymology Compounds": [
        {
          "Etymology Compound": "viola",
          "Compound Meaning": "violet"
        }
      ]
    }
  ]
}
```

With a definition sourced from [Wiktionary](https://en.wiktionary.org/wiki/ultraviolet):

```json
{
  "Word": "ultraviolet",
  "Definition": "of electromagnetic radiation beyond (higher in frequency than) light visible to the human eye; radiation with wavelengths from 380 nanometre - 10 nanometre",
  "Syllables": "ul tra vi o let",
  "Morpheme": [
    {
      "Morpheme": "ultra-",
      "Definition": "Beyond, outside of, as in ultrasonic.",
      "Etymology Compounds": [
        {
          "Etymology Compound": "uls",
          "Compound Meaning": "beyond"
        },
        {
          "Etymology Compound": "-ter",
          "Compound Meaning": "-ly; used to form adverbs from adjectives."
        },
        {
          "Etymology Compound": "-a",
          "Compound Meaning": "adverb"
        }
      ]
    },
    {
      "Morpheme": "violet",
      "Definition": "Having a bluish-purple colour.",
      "Etymology Compounds": [
        {
          "Etymology Compound": "viola",
          "Compound Meaning": "violet"
        }
      ]
    }
  ]
}
```

Results are generally better when the user gives the model an initial definition. This is mostly due to it giving the model a good initialization point. Though, depending on the word, it may not matter too much either way. 
