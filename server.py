# print('i love dahwin')
# import sys

# def print_python_version():
#     # Get the Python version
#     python_version = sys.version

#     # Print the Python version
#     print("Python Version:")
#     print(python_version)

# print_python_version()

# import time
# while True:
#     time.sleep(100)

text = """
import os
import sys
import time
import typing as t
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
# from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import asyncio
from typing import AsyncGenerator
import torch

app = FastAPI()





from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import asyncio
from queue import Queue
import threading
import re


model_cache = {}
tokenizer_cache = {}

class CustomTextStreamer:
    def __init__(self, tokenizer, text_queue, skip_prompt=False, **decode_kwargs):
        self.tokenizer = tokenizer
        self.text_queue = text_queue
        self.skip_prompt = skip_prompt
        self.decode_kwargs = decode_kwargs
        self.token_cache = []
        self.print_len = 0
        self.next_tokens_are_prompt = True

    def put(self, value):
        if len(value.shape) > 1 and value.shape[0] > 1:
            raise ValueError("TextStreamer only supports batch size 1")
        elif len(value.shape) > 1:
            value = value[0]

        if self.skip_prompt and self.next_tokens_are_prompt:
            self.next_tokens_are_prompt = False
            return

        self.token_cache.extend(value.tolist())
        text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)

        if text.endswith("\n"):
            printable_text = text[self.print_len:]
            self.token_cache = []
            self.print_len = 0
        elif len(text) > 0 and self._is_chinese_char(ord(text[-1])):
            printable_text = text[self.print_len:]
            self.print_len += len(printable_text)
        else:
            printable_text = text[self.print_len:text.rfind(" ") + 1]
            self.print_len += len(printable_text)

        self.on_finalized_text(printable_text)

    def end(self):
        if len(self.token_cache) > 0:
            text = self.tokenizer.decode(self.token_cache, **self.decode_kwargs)
            printable_text = text[self.print_len:]
            self.token_cache = []
            self.print_len = 0
        else:
            printable_text = ""

        self.next_tokens_are_prompt = True
        self.on_finalized_text(printable_text, stream_end=True)
        # Signal the end of the stream
        self.text_queue.put(None)

    def on_finalized_text(self, text, stream_end=False):
        if text:
            self.text_queue.put(text)

    def _is_chinese_char(self, cp):
        if (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0x20000 <= cp <= 0x2A6DF or
                0x2A700 <= cp <= 0x2B73F or 0x2B740 <= cp <= 0x2B81F or 0x2B820 <= cp <= 0x2CEAF or
                0xF900 <= cp <= 0xFAFF or 0x2F800 <= cp <= 0x2FA1F):
            return True
        return False








# Set the environment variable
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# Global variables to hold the model and tokenizer
model = None
tokenizer = None

def vllm_generate_iterator(
    llm, tokenizer, prompt: str, /, *, echo: bool = False, stop: str = None, stop_token_ids: t.List[int] = None, sampling_params=None, **attrs: t.Any
) -> t.Iterator[t.Dict[str, t.Any]]:
    request_id: str = attrs.pop('request_id', None)
    if request_id is None:
        raise ValueError('request_id must not be None.')
    if stop_token_ids is None:
        stop_token_ids = []

    eos_token_id = tokenizer.eos_token_id if hasattr(tokenizer, 'eos_token_id') else tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
    if eos_token_id is None:
        raise AttributeError("Tokenizer does not have 'eos_token_id' attribute or equivalent")
    stop_token_ids.append(eos_token_id)

    stop_ = set()
    if isinstance(stop, str) and stop != '':
        stop_.add(stop)
    elif isinstance(stop, list) and stop != []:
        stop_.update(stop)
    for tid in stop_token_ids:
        if tid:
            stop_.add(tokenizer.decode(tid))

    llm.add_request(request_id=request_id, prompt=prompt, sampling_params=sampling_params)

    while llm.has_unfinished_requests():
        for request_output in llm.step():
            for output in request_output.outputs:
                text = output.text
                yield {'text': text, 'error_code': 0, 'num_tokens': len(output.token_ids)}

            if request_output.finished:
                break

class Pipeline:
    def __init__(self, model_id, quantization, dtype):
        global model, tokenizer
        if model is None or tokenizer is None:
            tokenizer = AutoTokenizer.from_pretrained(model_id)


            def count_cuda_devices():
                if torch.cuda.is_available():
                    num_devices = torch.cuda.device_count()
                    return num_devices
                else:
                    return 0

            num_cuda_devices = count_cuda_devices()
            model = LLM(model=model_id, quantization=quantization, dtype=dtype, tensor_parallel_size=int(num_cuda_devices),max_model_len=4000,)
        self.tokenizer = tokenizer
        self.llm = model

    async def __call__(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 1.0,
        top_p: float = 0.95,
        top_k: int = 50,
        presence_penalty: float = 1.0,
        frequency_penalty: float = 0.0,
        repetition_penalty:float=1.1,
        prompt_template: str = "{prompt}",
        **kwargs,  # Passed to SamplingParams
    ) -> AsyncGenerator[str, None]:
        prompts = [
            (
                prompt_template.format(prompt=prompt),
                SamplingParams(
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    repetition_penalty=repetition_penalty,
                    stop_token_ids=[self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>")],  # KEYPOINT H
                    **kwargs,
                )
            )
        ]
        start = time.time()
        while True:
            if prompts:
                prompt, sampling_params = prompts.pop(0)
                gen = vllm_generate_iterator(self.llm.llm_engine, self.tokenizer, prompt, echo=False, stop=None, stop_token_ids=None, sampling_params=sampling_params, request_id="0")
                last = ""
                for x in gen:
                    if x['text'] == "":
                        continue
                    yield x['text'][len(last):]
                    last = x["text"]
                    num_tokens = x["num_tokens"]
                print(f"\nGenerated {num_tokens} tokens in {time.time() - start} seconds.")

                if not (self.llm.llm_engine.has_unfinished_requests() or prompts):
                    break

@app.post("/vllm")
async def generate(request: Request):
    request_data = await request.json()
    model_id = request_data.get("model_id")
    quantization = request_data.get("quantization")
    dtype = request_data.get("dtype")
    prompt = request_data.get("prompt")
    max_new_tokens = request_data.get("max_new_tokens", 512)
    temperature = request_data.get("temperature", 0.8)
    top_p = request_data.get("top_p", 0.95)
    top_k = request_data.get("top_k", 50)
    prompt_template = request_data.get("prompt_template", "{prompt}")

    pipe = Pipeline(model_id=model_id, quantization=quantization, dtype=dtype)

    async def stream_response():
        async for text in pipe(prompt=prompt, max_new_tokens=max_new_tokens, temperature=temperature, top_p=top_p, top_k=top_k, prompt_template=prompt_template):
            yield text

    return StreamingResponse(stream_response(), media_type="text/plain")







@app.post("/transformers")
async def generate(request: Request):
    request_data = await request.json()
    model_id = request_data.get("model_id")
    dtype = request_data.get("dtype", "float32")
    prompt = request_data.get("prompt")
    max_new_tokens = request_data.get("max_new_tokens", 512)
    temperature = request_data.get("temperature", 0.8)
    top_p = request_data.get("top_p", 0.95)
    top_k = request_data.get("top_k", 50)
    prompt_template = request_data.get("prompt_template", "{prompt}")

    if model_id not in tokenizer_cache:
        tokenizer_cache[model_id] = AutoTokenizer.from_pretrained(model_id)
    tokenizer = tokenizer_cache[model_id]

    if model_id not in model_cache:
        model_cache[model_id] = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=getattr(torch, dtype),
            device_map="auto",
        )
    model = model_cache[model_id]

    pattern = r"system\n(.+?)(?:\n\n|\Z)"
    match = re.search(pattern, prompt_template, re.DOTALL)
    system_message = match.group(1) if match else ""
    # Remove new lines
    system_message = system_message.replace('\n', '')
    messages = [
        {"role": "system", "content": f"{system_message}"},
        {"role": "user", "content": f"{prompt}"},
    ]
    
    print(messages)
    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    text_queue = Queue()

    async def stream_response(queue):
        while True:
            text = await asyncio.get_event_loop().run_in_executor(None, queue.get)
            if text is None:
                break
            yield text.encode('utf-8')

    streamer = CustomTextStreamer(tokenizer, text_queue, skip_prompt=True)
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]


    threading.Thread(target=model.generate, kwargs={
        "input_ids": input_ids,
        "max_new_tokens": max_new_tokens,
        "eos_token_id": terminators,
        "do_sample": True,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "streamer": streamer
    }).start()

    return StreamingResponse(stream_response(text_queue), media_type="text/plain")

@app.post("/restart")
async def restart_server():
    def restart():
        os.execl(sys.executable, sys.executable, *sys.argv)

    asyncio.create_task(asyncio.to_thread(restart))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
