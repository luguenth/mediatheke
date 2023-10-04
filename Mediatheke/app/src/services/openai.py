import json5
import logging
from typing import List
from ..mediaitem.model import MediaItem
from ..mediaitem.schemas import MediaItemSeries
from ...core.config import settings
import openai

logging.basicConfig(level=logging.INFO)

SCHEMA = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "List of mediaitems",
                "items": {
                    "type": "object",
                    "properties": {
                        "media_item_id": {
                            "type": "integer",
                            "description": "ID of the mediaitem"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the mediaitem"
                        },
                        "episode_number": {
                            "type": "integer",
                            "description": "Episode number of the mediaitem"
                        },
                        "season_number": {
                            "type": "integer",
                            "description": "Season number of the mediaitem"
                        },
                        "series_name": {
                            "type": "string",
                            "description": "Name of the series of the mediaitem"
                        }
                    }
                }
            }
        }
    }

def setup_openai(api_key: str):
    openai.api_key = api_key


def parse_items(items: list[dict]) -> list[MediaItemSeries]:
    """Refine the results from the GPT-3 response."""
    media_items_series = []
    for item in items:
        logging.info(item)
        try:
            media_items_series.append(MediaItemSeries(
                media_item_id=item["media_item_id"],
                title=item["title"],
                episode_number=item.get("episode_number", 0),
                season_number=item.get("season_number", 0),
                series_name=item.get("series_name", "")
            ))
        except Exception as e:
            logging.error(f"Couldn't parse or validate the data: {e}")
    return media_items_series


def send_to_gpt(prompt: str, functions: list):
    messages = [{"role": "user", "content": prompt}]
    try:
        logging.info("Sending to GPT")
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            functions=functions,
            function_call={"name": "parse_items"}
        )
    except Exception as e:
        logging.error(f"Exception: {repr(e)}")
        return None


def handle_gpt_response(response):
    if not response:
        return []

    response_message = response["choices"][0]["message"]
    finish_reason = response["choices"][0]["finish_reason"]

    if finish_reason == "length":
        logging.warning("GPT-3 returned an incomplete response. Aborting.")
        return []

    function_call_data = response_message.get("function_call")
    if not function_call_data:
        return []

    function_name = function_call_data["name"]
    function_args = json5.loads(function_call_data["arguments"])

    return parse_items(items=function_args.get("items"))


def run_conversation(items: list[MediaItem]) -> list[MediaItemSeries]:
    setup_openai(api_key=settings.openai_key)
    prompt = "Here is a List of Mediaitems, try to spot the episodes of a Series... \n"
    prompt += "\n".join(
        [f"{item.id}: {item.title} | {item.topic} | {item.channel} | {item.description} | {item.date} | {item.duration}"
         for item in items]
    )

    response = send_to_gpt(prompt, functions=[{"name": "parse_items", "parameters": SCHEMA}])
    return handle_gpt_response(response)
