import json
import csv
from typing import List, Dict
from question_generator import QuestionGenerator

class BatchQuestionProcessor:
    def __init__(self):
        self.generator = QuestionGenerator()
    
    def process_text_file(self, file_path: str) -> Dict:
        """Process a text file and generate questions for each paragraph"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            results = {
            for i, paragraph in enumerate(paragraphs, 1):
                if len(paragraph) >= 50:  # Only process substantial paragraphs
                    questions = self.generator.generate_questions(paragraph)
                    results[f"Paragraph_{i}"] = {
                        "text": paragraph,
                        "questions": questions
                    }
            
            return results
        
        except FileNotFoundError:
            return {"error": f"File {file_path} not found"}
        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}
    
    def save_to_json(self, results: Dict, output_file: str):
        """Save results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
        print(f"✅ Results saved to {output_file}")
    
    def save_to_csv(self, results: Dict, output_file: str):
        """Save results to CSV file"""
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Paragraph_ID', 'Original_Text', 'Question_Type', 'Question', 'Options', 'Answer'])
            
            for para_id, data in results.items():
                if 'questions' in data:
                    text = data['text'][:100] + "..." if len(data['text']) > 100 else data['text']
                    
                    for question_type, questions in data['questions'].items():
                        if question_type == "Key Phrases Identified":
                            continue
                        elif question_type == "Multiple Choice Questions":
                            for q in questions:
                                options = " | ".join(q['options'])
                                answer = q['options'][q['correct_answer_index']]
                                writer.writerow([para_id, text, question_type, q['question'], options, answer])
                        elif question_type == "Fill in the Blank Questions":
                            for q in questions:
                                writer.writerow([para_id, text, question_type, q['question'], "", q['answer']])
                        else:
                            for question in questions:
                                writer.writerow([para_id, text, question_type, question, "", ""])
        
        print(f"✅ Results saved to {output_file}")

def demo_batch_processing():
    """Demonstrate batch processing capabilities"""
    print("📦 Batch Question Generator Demo")
    print("=" * 40)
    
    # Create sample content
    sample_content = """
Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, scientific evidence shows that human activities have been the main driver of climate change since the 1800s. The burning of fossil fuels generates greenhouse gas emissions that act like a blanket wrapped around Earth, trapping the sun's heat and raising temperatures.

Renewable energy sources such as solar, wind, and hydroelectric power offer sustainable alternatives to fossil fuels. These technologies have become increasingly cost-effective and efficient over the past decade. Solar panels can now convert sunlight into electricity at unprecedented rates, while wind turbines have grown larger and more powerful. The transition to renewable energy is crucial for reducing carbon emissions and combating climate change.

Artificial intelligence is transforming industries across the globe. Machine learning algorithms can analyze vast amounts of data to identify patterns and make predictions. In healthcare, AI assists in diagnosing diseases and developing personalized treatment plans. In transportation, autonomous vehicles use AI to navigate safely through complex environments. As AI technology continues to evolve, it promises to revolutionize how we work, communicate, and solve complex problems.
    """
    
    # Save sample content to a temporary file
    with open('sample_content.txt', 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    # Process the file
    processor = BatchQuestionProcessor()
    results = processor.process_text_file('sample_content.txt')
    
    # Display results
    for para_id, data in results.items():
        print(f"\n📄 {para_id}:")
        print(f"Text: {data['text'][:100]}...")
        print("\nGenerated Questions:")
        
        for question_type, questions in data['questions'].items():
            if question_type == "Key Phrases Identified":
                continue
            elif question_type == "Multiple Choice Questions":
                print(f"\n  {question_type}:")
                for i, q in enumerate(questions, 1):
                    print(f"    {i}. {q['question']} [{q['marks']} marks]")
                    for j, option in enumerate(q['options']):
                        print(f"       {chr(97+j)}) {option[:50]}..." if len(option) > 50 else f"       {chr(97+j)}) {option}")
                    print(f"       Correct Answer: {chr(97+q['correct_answer_index'])})")
            elif question_type == "Fill in the Blank Questions":
                print(f"\n  {question_type}:")
                for i, q in enumerate(questions, 1):
                    print(f"    {i}. {q['question']} [{q['marks']} marks]")
                    print(f"       Answer: {q['answer']}")
            else:
                print(f"\n  {question_type}:")
                for i, q in enumerate(questions, 1):
                    print(f"    {i}. {q['question']} [{q['marks']} marks]")
    
    # Save results
    processor.save_to_json(results, 'questions_output.json')
    processor.save_to_csv(results, 'questions_output.csv')
    
    print(f"\n✨ Processed {len(results)} paragraphs successfully!")

if __name__ == "__main__":
    demo_batch_processing()
