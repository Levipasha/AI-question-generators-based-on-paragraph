import sys
from question_generator import QuestionGenerator

def interactive_mode():
    """Interactive mode for the question generator"""
    print("🎯 Interactive AI Question Generator")
    print("=" * 40)
    print("Enter 'quit' to exit the program")
    print("Enter 'help' for usage instructions")
    print("-" * 40)
    
    generator = QuestionGenerator()
    
    while True:
        print("\n📝 Enter your paragraph:")
        user_input = input().strip()
        
        if user_input.lower() == 'quit':
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("\n💡 Help:")
            print("- Enter a paragraph (at least 50 characters)")
            print("- The AI will generate factual, analytical, and comprehension questions")
            print("- Type 'quit' to exit")
            print("- Type 'help' to see this message again")
            continue
        elif len(user_input) < 50:
            print("⚠️  Please enter a longer paragraph (at least 50 characters)")
            continue
        
        print("\n🔄 Generating questions...")
        questions = generator.generate_questions(user_input)
        
        # Display results
        for category, question_list in questions.items():
            if category == "error":
                print(f"❌ Error: {question_list[0]}")
                continue
            
            print(f"\n📋 {category}:")
            print("-" * (len(category) + 5))
            
            if category == "Key Phrases Identified":
                for i, phrase in enumerate(question_list, 1):
                    print(f"  {i}. {phrase}")
            elif category == "Multiple Choice Questions":
                for i, q in enumerate(question_list, 1):
                    print(f"  {i}. {q['question']} [{q['marks']} marks]")
                    for j, option in enumerate(q['options']):
                        print(f"     {chr(97+j)}) {option}")
                    print(f"     Correct Answer: {chr(97+q['correct_answer_index'])})")
            elif category == "Fill in the Blank Questions":
                for i, q in enumerate(question_list, 1):
                    print(f"  {i}. {q['question']} [{q['marks']} marks]")
                    print(f"     Answer: {q['answer']}")
            else:
                for i, q in enumerate(question_list, 1):
                    print(f"  {i}. {q['question']} [{q['marks']} marks]")

        print("\n" + "-" * 40)

if __name__ == "__main__":
    interactive_mode()
