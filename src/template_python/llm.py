from functools import cached_property
from pathlib import Path
from typing import Type, TypeVar, Literal

import instructor
from ollama import Client
from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from template_python.utils.logger import log


_StructuredOutput = TypeVar("_StructuredOutput", bound=BaseModel)


class LLM:
    __last_completion: dict[Literal["prompt", "completion"], int] = {
        "prompt": 0,
        "completion": 0,
    }
    SYSTEM: str = "You are a helpful assistant."

    def __init__(
        self,
        base_url: str = "http://100.99.54.84:11434/v1",
        model: str = "general_small",
        api_key: str = "ollama",
        **kwargs,
    ) -> None:
        try:
            self.__api_base: str = base_url
            self.__model = model
            self.__openai = OpenAI(
                base_url=self.__api_base,
                api_key=api_key,
                **kwargs,
            )
            self.__instructor = instructor.from_openai(
                self.__openai, mode=instructor.Mode.JSON
            )

            _host = "//".join(Path(self.__api_base).parts[:2])
            if _host.casefold() == "https://api.openai.com":
                self.__ollama = None
            else:
                self.__ollama = Client(host=_host)

        except Exception as e:
            log.critical(f"Exception in `LLM.__init__({kwargs=})`\n{e}")
            raise e

    def response(
        self, messages: list[dict[str]], model: str | None = None, **kwargs
    ) -> str:
        """Get ChatCompletions text from LLM

        Args:
            messages (list[dict[str]]): Input messages
            model (str | None, optional): Name of Model or `None`. Defaults to None.

        Returns:
            str: Response content
        """
        _inputs = {
            "model": model or self.__model,
            "messages": messages,
            "stream": False,
            "temperature": 0,
        }
        for k, v in kwargs.items():
            _inputs[k] = v

        try:
            response = self.__openai.chat.completions.create(**_inputs)

            if _inputs["stream"]:
                res_text = ""
                for chunk in response:
                    if res_text == "":
                        log.debug("Streaming response started.")
                    res_text += chunk.choices[0].delta.content or ""
            else:
                res_text = response.choices[0].message.content
                self.__update_token_usage(response=response)
            log.info("Chat response received")
            log.debug(f"Response: {res_text}")
            return res_text
        except Exception as e:
            log.critical(f"Error encountered in `LLM.response({_inputs=})`")
            log.critical(str(e))
            raise e

    def structured_response(
        self,
        messages: list[dict[str]],
        response_model: Type[_StructuredOutput],
        model: str | None = None,
    ) -> _StructuredOutput:
        """Chat with LLM to get structured response

        Args:
            messages (list[dict[str]]): `system`, `user` and `assistant`(optional) messages to pass to LLM
            response_model (Type[_StructuredOutput]): Pydantic model for validation
            model (str | None, optional): Name of model. Defaults to model defined in config.toml.

        Returns:
            _StructuredOutput: Instance of `response_model`.
        """

        messages[-1]["content"] += ". return as JSON."
        _inputs = {
            "model": model or self.__model,
            "messages": messages,
            "response_model": response_model,
            "temperature": 0,
        }
        try:
            return self.__instructor.chat.completions.create(**_inputs)
        except Exception as e:
            log.critical(f"Exception in `LLM.structured_response({_inputs=})`\n{e}")
            raise e

    @cached_property
    def models(self) -> list[str]:
        """Get the list of available models"""
        try:
            return [x.id for x in self.__openai.models.list().data]
        except Exception as e:
            log.critical("Exception in `LLM.models`\n{e}")
            raise e

    def __update_token_usage(self, response: ChatCompletion):
        self.__last_completion = {
            "prompt": response.usage.completion_tokens,
            "completion": response.usage.prompt_tokens,
        }

    def msg(self, user_content: str) -> list[dict[str]]:
        """Generate `messages` based on default `self.SYSTEM` message]"""
        return [
            {"role": "system", "content": self.SYSTEM},
            {"role": "user", "content": user_content},
        ]

    def unload_all(self) -> None:
        """Unload all models from VRAM"""
        for model in self.loaded_models:
            self.__ollama.chat(
                model=model, messages=[{"role": "user", "content": ""}], keep_alive=0
            )
        return

    @property
    def loaded_models(self) -> list[str]:
        """List the models loaded to VRAM"""
        if self.__ollama is not None:
            return [modelinfo.model for modelinfo in self.__ollama.ps().models]
        return []

    def __str__(self) -> str:
        return f"LLM(api_base={self.__api_base}, model={self.__model})"

    def estimate_cost(
        self,
        input_cost: float,
        output_cost: float,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> float:
        """Estimate the cost of a prompt and completion

        Args:
            input_cost (float): Cost per token for input
            output_cost (float): Cost per token for output
            input_tokens (int | None, optional): # of input tokens. Defaults to previous input.
            output_tokens (int | None, optional): # of output tokens. Defaults to previous output.

        Returns:
            float: Total Cost
        """
        if input_tokens is not None:
            input_tokens = self.__last_completion["prompt"]
        if output_tokens is not None:
            output_tokens = self.__last_completion["completion"]

        return (input_tokens * input_cost) + (output_tokens * output_cost)
