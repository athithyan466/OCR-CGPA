import torch
from transformers import (
    Qwen2_5_VLForConditionalGeneration,
    AutoProcessor
)

from PIL import Image
import cv2


MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

print("Loading Qwen2.5-VL...")

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    trust_remote_code=True
)

print("Model Loaded.")
def read_marksheet(image_path):

    prompt = """
You are an OCR engine.

Read the result table EXACTLY as it appears.

IMPORTANT RULES

1. NEVER infer.
2. NEVER guess.
3. NEVER modify any value.
4. NEVER change the Sem column.
5. Copy the Sem value EXACTLY from the table.
6. Read EVERY row.
7. Ignore only the page header, disclaimer and footer.

Extract these columns only:

Sem
Course Code
Course Name
Credits
Grade

Read the Grade ONLY from the 'GR.' column.

Ignore:

Part
Result
GP
SGPA
CGPA

Return ONLY JSON.

Format:

{
    "subjects":[
        {
            "sem":"",
            "subject_code":"",
            "subject_name":"",
            "credits":"",
            "grade":""
        }
    ]
}

Do not explain.

Do not wrap the JSON inside ```.

Return JSON only.
"""

 
    print("Creating prompt...")
    if isinstance(image_path, str):
         image = Image.open(image_path).convert("RGB")
    else:
        image = cv2.cvtColor(image_path, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
    print("Creating prompt...")
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }
    ]

    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    print("Creating inputs...")

    inputs = processor(
        text=[text],
        images=[image],
        return_tensors="pt",
        padding=True
    )
    print("Generating...")

    inputs = inputs.to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False
        )

    generated_ids_trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    print("Decoding...")
    result = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )[0]

    return result
