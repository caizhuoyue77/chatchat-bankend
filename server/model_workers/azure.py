import sys
from fastchat.conversation import Conversation
from server.model_workers.base import *
from server.utils import get_httpx_client
from fastchat import conversation as conv
import json
from typing import List, Dict


class AzureWorker(ApiModelWorker):
    def __init__(
            self,
            *,
            controller_addr: str,
            worker_addr: str,
            model_names: List[str] = ["azure-api"],
            version: str = "gpt-3.5-turbo-16K",
            **kwargs,
    ):
        kwargs.update(model_names=model_names, controller_addr=controller_addr, worker_addr=worker_addr)
        kwargs.setdefault("context_len", 16384)  # TODO 16K模型需要改成16384
        super().__init__(**kwargs)
        self.version = version

    def do_chat(self, params: ApiChatParams) -> Dict:
        params.load_config(self.model_names[0])
        data = dict(
            model="gpt-3.5-turbo-16k",
            # model="gpt-3.5-turbo",
            messages=params.messages,
            temperature=params.temperature,
            max_tokens=2000,
            stream=True,
        )
        # url = ("https://{}.openai.azure.com/openai/deployments/{}/chat/completions?api-version={}"
        #        .format(params.resource_name, params.deployment_name, params.api_version))
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Accept': 'application/json',
        #     'api-key': params.api_key,
        # }

        API_KEY = "sb-0ed569a255461d5fc8304e26dc11250c6b1adad270a62785"
        url = "https://api.openai-sb.com/v1/chat/completions"
        headers = {
            'Authorization': f"Bearer {API_KEY}",
            'Content-type': 'application/json',
        }

        text = ""
        with get_httpx_client() as client:
            # print(data)
            # print(headers)
            with client.stream("POST", url, headers=headers, json=data) as response:
                # print(response)
                for line in response.iter_lines():
                    if not line.strip() or "[DONE]" in line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    resp = json.loads(line)
                    if choices := resp["choices"]:
                        if chunk := choices[0].get("delta", {}).get("content"):
                            text += chunk
                            yield {
                                "error_code": 0,
                                "text": text
                            }

    def get_embeddings(self, params):
        # TODO: 支持embeddings
        print("embedding")
        print(params)

    def make_conv_template(self, conv_template: str = None, model_path: str = None) -> Conversation:
        # TODO: 确认模板是否需要修改
        return conv.Conversation(
            name=self.model_names[0],
            system_message="You are a helpful, respectful and honest assistant.",
            messages=[],
            roles=["user", "assistant"],
            sep="\n### ",
            stop_str="###",
        )


if __name__ == "__main__":
    import uvicorn
    from server.utils import MakeFastAPIOffline
    from fastchat.serve.base_model_worker import app

    worker = AzureWorker(
        controller_addr="http://127.0.0.1:20001",
        worker_addr="http://127.0.0.1:21008",
    )
    sys.modules["fastchat.serve.model_worker"].worker = worker
    MakeFastAPIOffline(app)
    uvicorn.run(app, port=21008)
