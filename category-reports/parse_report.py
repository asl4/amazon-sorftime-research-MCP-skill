import sys
import json
import codecs
import re

# Read the saved response
with open('category-reports/kids-drawing-kits-raw.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract data from SSE format
for line in content.split('\n'):
    if line.startswith('data: '):
        json_str = line[6:]  # Remove 'data: ' prefix
        try:
            data = json.loads(json_str)
            text = data['result']['content'][0]['text']
            # Decode unicode escaped text
            text = codecs.decode(text, 'unicode-escape')
            # Parse the nested JSON
            report = json.loads(text)
            print(json.dumps(report, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
