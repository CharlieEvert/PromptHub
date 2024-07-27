import os
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)
from datasets import Dataset, DatasetDict
from ragas import evaluate
import nest_asyncio
import pandas as pd
from dotenv import load_dotenv

#get your OpenAI API Key
load_dotenv('/.env') 
api_key = os.environ.get("OPENAI_API_KEY")

# Apply nest_asyncio to allow nested event loops, for use with Anaconda. If running in terminal, uncomment below.
# nest_asyncio.apply()

data = {
    'question': [
        'When was the first moon landing?',
        'Who is the CEO of Tesla?',
        'What is the capital of France?',
        'Who wrote "To Kill a Mockingbird"?',
        'What is the boiling point of water?',
        'Who painted the Mona Lisa?',
        'What is the largest planet in our solar system?',
        'Who invented the telephone?',
        'What is the chemical symbol for gold?',
        'Who was the first president of the United States?'
    ],
    'ground_truth': [
        'The first moon landing was on July 20, 1969.',
        'Elon Musk is the CEO of Tesla.',
        'The capital of France is Paris.',
        'Harper Lee wrote "To Kill a Mockingbird".',
        'The boiling point of water is 100 degrees Celsius or 212 degrees Fahrenheit at sea level.',
        'Leonardo da Vinci painted the Mona Lisa.',
        'Jupiter is the largest planet in our solar system.',
        'Alexander Graham Bell invented the telephone.',
        'The chemical symbol for gold is Au.',
        'George Washington was the first president of the United States.'
    ],
    'answer': [
        'The first successful Mars landing occurred in the late 20th century.',
        'Bill Gates founded Microsoft and is currently leading various philanthropic efforts.',
        'The capital of France is London, known for its iconic Eiffel Tower.',
        'William Shakespeare, the famous English playwright, wrote "To Kill a Mockingbird" in the 16th century.',
        'Water boils at 150 degrees Celsius, which is why it is used in cooking.',
        'The Mona Lisa was painted by Vincent van Gogh during his blue period.',
        'Saturn, with its beautiful rings, is the largest planet in the Milky Way galaxy.',
        'Thomas Edison, the prolific inventor, created the first telephone in his laboratory.',
        'The chemical symbol for gold is GO, representing its golden color.',
        'Benjamin Franklin, known for his experiments with electricity, was the first US president.'
    ],
    'contexts': [
        ['The Apollo program was a series of space missions conducted by NASA.', 'Neil Armstrong was an American astronaut.'],
        ['SpaceX is a private space exploration company.', 'Jeff Bezos is the founder of Amazon and Blue Origin.'],
        ['The Louvre is a famous museum in Paris.', 'French cuisine is renowned worldwide for its sophistication.'],
        ['The Pulitzer Prize is a prestigious award for achievements in newspaper, magazine, online journalism, literature, and musical composition.', 'Truman Capote was an American novelist, short story writer, screenwriter, playwright, and actor.'],
        ['The triple point of water is the temperature and pressure at which the three phases of water coexist in thermodynamic equilibrium.', 'Evaporation is the process of a substance in a liquid state changing to a gaseous state.'],
        ['Renaissance art flourished in Italy during the 14th to 17th centuries.', 'Impressionism was an art movement that originated in 19th-century France.'],
        ['A planet is a celestial body that orbits a star and has cleared its orbital path of other objects.', 'Pluto was reclassified as a dwarf planet in 2006.'],
        ['Morse code is a method used in telecommunication to encode text characters as standardized sequences of two different signal durations.', 'The industrial revolution saw a rapid development of new technologies.'],
        ['The periodic table is a tabular display of the chemical elements.', 'Alchemy was an ancient branch of natural philosophy, a philosophical and protoscientific tradition.'],
        ['The American Revolution was a colonial revolt that took place between 1765 and 1783.', 'The Constitution of the United States is the supreme law of the United States of America.']
    ]
}

# Create Dataset object
custom_dataset = Dataset.from_dict(data)

# Create DatasetDict
custom_dataset_dict = DatasetDict({"eval": custom_dataset})

# Perform the evaluation
result = evaluate(
    custom_dataset_dict["eval"],
    metrics=[
        context_precision,
        faithfulness,
        answer_relevancy,
        context_recall,
    ],
    raise_exceptions=False  # Continue execution despite exceptions
)

df = result.to_pandas()
