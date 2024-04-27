import json
import re
from typing import Dict, Optional


class JsonUtility(object):

    @classmethod
    def extract_json_block(cls, text: str) -> Optional[Dict]:
        pattern = r'```(.*?)\n(.*?)```'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        if len(code_blocks) == 0:
            return None
        json_data = code_blocks[0][1]
        return json.loads(json_data)
