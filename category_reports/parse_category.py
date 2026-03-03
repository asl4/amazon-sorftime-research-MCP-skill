import json
import codecs
import sys
import re

# Read the file
with open('C:/Users/49707/.claude/projects/D--amazon-mcp/4700d6ba-1f24-46ad-a7eb-86635bb4d208/tool-results/bjfkes1xv.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the data: part
for line in content.split('\n'):
    if line.startswith('data: '):
        json_text = line[6:]  # Remove 'data: ' prefix
        try:
            data = json.loads(json_text)
            result_text = data['result']['content'][0]['text']

            # Decode unicode escape
            result_text = codecs.decode(result_text, 'unicode-escape')

            # Parse the nested JSON - extract just the JSON part more carefully
            # Find the start and end of the JSON object
            start = result_text.find('{')
            if start != -1:
                # Find matching closing brace
                depth = 0
                end = -1
                for i in range(start, len(result_text)):
                    if result_text[i] == '{':
                        depth += 1
                    elif result_text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break

                if end != -1:
                    json_str = result_text[start:end]
                    # Clean control characters that could cause parsing issues
                    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                    category_data = json.loads(json_str)

                # Save to file
                with open('C:/Users/49707/.claude/projects/D--amazon-mcp/category_data.json', 'w', encoding='utf-8') as out:
                    json.dump(category_data, out, ensure_ascii=False, indent=2)

                print('Data parsed and saved to category_data.json')

                # Print category statistics
                if 'Top100产品' in category_data:
                    products = category_data['Top100产品']
                    print(f'\nTotal products: {len(products)}')
                    print(f'\nTop 20 ASINs:')
                    for i, p in enumerate(products[:20]):
                        title = p.get('标题', '')[:50]
                        print(f'{i+1}. {p["ASIN"]} - {title}... - Price: ${p.get("价格", 0)}')

                # Print statistics
                print(f'\n=== Category Statistics ===')
                for key, value in category_data.items():
                    if key != 'Top100产品':
                        print(f'{key}: {value}')
                break
        except Exception as e:
            print(f'Error parsing line: {e}')
            import traceback
            traceback.print_exc()
            continue
