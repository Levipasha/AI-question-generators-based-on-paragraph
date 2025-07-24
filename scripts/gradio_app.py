import gradio as gr
import json
from question_generator import QuestionGenerator, download_nltk_data

print("Starting the Gradio application...")

# Ensure NLTK data is available before starting
print("Checking for NLTK data...")
download_nltk_data()
print("NLTK data check complete.")

# Instantiate the generator once to load models, etc.
print("Initializing Question Generator...")
generator = QuestionGenerator()
print("Question Generator initialized.")

def format_questions(questions_dict):
    """Formats the generated questions for display in Markdown."""
    output = ""
    for category, question_list in questions_dict.items():
        if category == "Key Phrases Identified":
            continue # We can display these differently if needed, or just omit them for now

        output += f"### {category}\n"
        output += "---\n"

        if not question_list:
            output += "_No questions generated for this category._\n\n"
            continue

        if category == "Multiple Choice Questions":
            for i, q in enumerate(question_list, 1):
                output += f"**{i}. {q['question']}** ({q['marks']} marks)\n"
                for j, option in enumerate(q['options']):
                    output += f"   - {chr(97+j)}) {option}\n"
                output += f"   - **Correct Answer:** {chr(97+q['correct_answer_index'])})\n\n"
        elif category == "Fill in the Blank Questions":
            for i, q in enumerate(question_list, 1):
                output += f"**{i}. {q['question']}** ({q['marks']} marks)\n"
                output += f"   - **Answer:** {q['answer']}\n\n"
        else:
            for i, q in enumerate(question_list, 1):
                output += f"**{i}. {q['question']}** ({q['marks']} marks)\n\n"
    return output

def generate_questions_from_text(paragraph):
    """
    Takes a paragraph of text and returns a formatted string of questions.
    """
    if not paragraph or len(paragraph.strip()) < 50:
        return "Please enter a paragraph with at least 50 characters."
        
    # Generate questions using the existing generator
    questions = generator.generate_questions(paragraph)
    
    # Format the questions for display
    formatted_output = format_questions(questions)
    
    return formatted_output

# Create the Gradio interface
iface = gr.Interface(
    fn=generate_questions_from_text,
    inputs=gr.Textbox(lines=10, placeholder="Enter a paragraph here...", label="Input Text"),
    outputs=gr.Markdown(label="Generated Questions"),
    title="📝 AI Question Generator",
    description="Enter a paragraph of text (at least 50 characters) to generate various types of questions. The model will produce factual, analytical, multiple-choice, and other question types based on the input.",
    allow_flagging="never",
    theme="soft"
)

if __name__ == "__main__":
    iface.launch(server_port=7861)
