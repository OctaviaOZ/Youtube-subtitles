import os
import sys
import openai
import re

def get_openai_api_key():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return openai_api_key

def extract_unique_sentences_from_vtt(vtt_content):
    # Split the content into blocks based on timestamps
    blocks = re.split(r'\d{2}:\d{2}:\d{2}\.\d{3} --\> \d{2}:\d{2}:\d{2}\.\d{3}', vtt_content)

    unique_sentences = []
    last_sentence = ''
    for block in blocks:
        # Clean each block to remove metadata and keep only the text
        block = re.sub(r'align:start position:\d+%\n', '', block)
        block = re.sub(r'<.*?>', '', block).strip()

        # Skip empty blocks
        if block:
            sentences = block.split('\n')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and sentence != last_sentence:
                    unique_sentences.append(sentence)
                    last_sentence = sentence

    # Join the unique sentences into a single text
    unique_text = '\n'.join(unique_sentences)
    return unique_text

def convert_text(text):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that converts text to a well-structured human-readable format in the original language."},
            {"role": "user", "content": f"Convert the following text to a well-structured human-readable format in the original language:\n\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def translate_text(text, target_language='Ukrainian'):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are an assistant that translates text to {target_language}."},
            {"role": "user", "content": f"Translate the following text to {target_language}:\n\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def save_file(file_path, content):
    """
    Save the given content to a file at the specified path.
    """
    with open(file_path, 'w') as output_file:
        output_file.write(content)
        print(f"Result saved to {file_path}")

def main():
    # Check if the VTT file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <vtt_file_path>")
        return

    vtt_file_path = sys.argv[1]

    # Read the VTT file
    with open(vtt_file_path, 'r') as file:
        vtt_content = file.read()

    # Extract unique sentences
    unique_sentences_text = extract_unique_sentences_from_vtt(vtt_content)

    # Save the result to a new text file
    output_file_path = os.path.splitext(vtt_file_path)[0] + "_temp.txt"
    with open(output_file_path, 'w') as output_file:
        output_file.write(unique_sentences_text)

    # Get the OpenAI API key from the environment variable
    openai_api_key = get_openai_api_key()
    openai.api_key = openai_api_key

    structured_text = convert_text(unique_sentences_text)
    # Save the structured text to a file
    structured_file_path = os.path.splitext(vtt_file_path)[0] + "_ge.txt"
    save_file(structured_file_path, structured_text)


    translated_text = translate_text(structured_text)
    # Save the result to a new text file
    translated_file_path = os.path.splitext(vtt_file_path)[0] + "_ua.txt"
    save_file(translated_file_path, translated_text)



if __name__ == "__main__":
    main()