import asyncio
import json
from pathlib import Path

import pytest
import skill_newyear_quest
import skill_newyear_quest.application
import skill_newyear_quest.phrases
import skill_newyear_quest.quest

base_req_file_name = Path(__file__).parent / "base_request.json"


class FakeRequest:
    def __init__(self, json):
        self._json = json

    async def json(self):
        await asyncio.sleep(0.001)
        return self._json


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phrase_text, new_session, answer",
    [
        ("новогодний квест", True, skill_newyear_quest.phrases.HELLO_PHRASES[0][0]),
        ("да", False, "001"),
        ("звездочёт", False, "101"),
        ("библиотека", False, "201"),
        ("историю", False, "306"),
    ],
)
async def test_skill(phrase_text, new_session, answer):

    req = {}
    with open(base_req_file_name) as f:
        req = json.load(f)

    req["request"]["command"] = phrase_text
    req["session"]["new"] = new_session

    resp = await skill_newyear_quest.application.marusya_newyear_quest(FakeRequest(req))
    if new_session:
        assert json.loads(resp.text)["response"]["text"] in answer
    else:
        skill_newyear_quest.quest.get_stage_by_id(answer).texts[0] in json.loads(
            resp.text
        )["response"]["text"]
