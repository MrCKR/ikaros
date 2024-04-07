import re
from openai import OpenAI

language_name = 'Chinese'
client = OpenAI(
    # This is the default and can be omitted
    # api_key='sk-4UGE3NbX0U2PGSSRS2U50sVMhMoocjX0I17gmclFmXfY04vN',
    # base_url= 'https://api.chatanywhere.tech/v1'
)


def translate_text(text):
    if not text: 
        return text
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate the following subtitle text into {language_name}, but keep the subtitle number and timeline unchanged: \n{text}",
                    }
                ],
            )
            t_text = completion.choices[0].message.content
            if is_translation_valid(text,t_text ):
                return t_text
            else:
                retries += 1
        except Exception as e:
            import time
            sleep_time = 60
            time.sleep(sleep_time)
            retries += 1
    return text
    

def is_translation_valid(original_text, translated_text):
    def get_index_lines(text):
        lines = text.split('\n')
        index_lines = [line for line in lines if re.match(r'^\d+$', line.strip())]
        return index_lines
    original_index_lines = get_index_lines(original_text)
    translated_index_lines = get_index_lines(translated_text)
    return original_index_lines == translated_index_lines
