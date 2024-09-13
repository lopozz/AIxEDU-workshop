import re

import os

def read_and_replace_text_file(file_path):
    data = {
        'dialogue': '',
        'question': '',
        'options': []
    }

    # Check if the filename contains "conversation" or "lecture"
    file_name = os.path.basename(file_path)

    # If "conversation" is in the file name, toggle between Speaker A and B
    is_conversation = 'conversation' in file_name.lower()
    
    current_speaker = 'Speaker A:'  # Start with Speaker A

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading and trailing whitespace

            if line.startswith('SENTENCE'):
                sentence = line[len('SENTENCE '):].strip()

                if is_conversation:
                    # For "conversation" files, toggle speakers and add them to dialogue
                    # data['dialogue'] += ' '.join((current_speaker, sentence)) + '\n'
                    data['dialogue'] += sentence + '\n'
                    # Toggle the speaker for the next sentence
                    current_speaker = 'Speaker A:' if current_speaker == 'Speaker B:' else 'Speaker B:'
                else:
                    # For "lecture" files, just concatenate the text without adding speaker labels
                    data['dialogue'] += sentence.capitalize() + ' '

            elif line.startswith('QUESTION'):
                # Extract the question after 'QUESTION '
                data['question'] = line[len('QUESTION '):].strip()
            elif line.startswith('OPTION'):
                # Extract the option text and its label (0 or 1)
                option_text = line[len('OPTION '):].strip()
                option, label = option_text.rsplit(' ', 1)  # Split text and label
                data['options'].append({'option': option, 'label': int(label)})

        # Find the correct and incorrect answers based on the label
        data['correct_answer'] = [c['option'] for c in data['options'] if c['label'] == 1][0]
        data['incorrect_answer'] = [c['option'] for c in data['options'] if c['label'] == 0][0]

    return data


def extract_agent_output(log_text, agent_name="Student Mind Reader Machine", executor_marker="Entering new CrewAgentExecutor chain...", final_marker="Thought"):
    # Define the start marker where extraction should begin
    start_marker = f"Working Agent: {agent_name}"
    executor_marker = executor_marker
    
    # Regular expression to capture everything from the executor marker to the last occurrence of "Thought"
    pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(executor_marker)}(.*?)(\nThought.*?(\n.*)?)(?=\n\S|\Z)", re.DOTALL)
    
    # Search for the pattern in the log text
    match = pattern.search(log_text)
    
    if match:
        # Extract the text and clean it up if needed
        return match.group(1) + match.group(2)
    else:
        return None  # Return None if no match is found

def extract_student_mind_reader_output(text):
    # Split the text into lines
    lines = text.split('\n')
    
    # Flag to indicate when we've found the relevant section
    found_section = False
    
    # List to store the relevant lines
    output_lines = []
    
    # Variable to keep track of the last "Thought:" line
    last_thought_index = -1
    
    for i, line in enumerate(lines):
        if "Working Agent: Student Mind Reader Machine" in line:
            found_section = True
            continue
        
        if found_section:
            if line.strip().startswith("Thought:"):
                last_thought_index = len(output_lines)
            
                output_lines.append(line)
            
            if line.strip().startswith("Final Answer:"):
                break
    
    # If we found a "Final Answer:", trim the output to the last "Thought:"
    if last_thought_index != -1:
        output_lines = output_lines[:last_thought_index + 1]
    
    # Join the relevant lines back into a single string
    return '\n'.join(output_lines).strip()


def add_to_markdown_file(extracted_text, markdown_file_path):
    try:
        # Read the existing content of the Markdown file
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            existing_content = file.read()
        
        extracted_text = '\n\n'.join(extracted_text.replace('Thought:', '**Thought**:').split('\n'))
        # Prepare the new content
        new_content = f"{extracted_text}\n\n---\n\n{existing_content}"
        
        # Write the new content back to the file
        with open(markdown_file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Successfully added the extracted text to {markdown_file_path}")
    except IOError as e:
        print(f"An error occurred while working with the file: {e}")


# print(read_and_replace_text_file('src/data/tpo_26-conversation_1_1')['dialogue'])