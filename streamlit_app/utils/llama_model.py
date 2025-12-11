import torch
from transformers import pipeline
from dotenv import loadenv
import os

loadenv()


model_id = "meta-llama/Llama-3.2-1B"
HUGGING_FACE_API = os.environ.get("HUGGING_FACE_API", None)

if not HUGGING_FACE_API:
    raise ValueError("HUGGING_FACE_API environment variable not set")

pipe = pipeline(
    "text-generation", 
    model=model_id, 
    torch_dtype=torch.bfloat16, 
    device_map="auto"
)

def get_actual_keyowrds(tokens):


pipe("The key to life is")
