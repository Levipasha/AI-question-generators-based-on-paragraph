import re
import random
from typing import List, Dict, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.corpus import stopwords
from collections import Counter

def download_nltk_data():
    """Downloads all necessary NLTK data models."""
    packages = [
        ('tokenizers/punkt', 'punkt'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
        ('chunkers/maxent_ne_chunker', 'maxent_ne_chunker'),
        ('corpora/words', 'words'),
        ('corpora/stopwords', 'stopwords')
    ]
    for path, package_id in packages:
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"NLTK package '{package_id}' not found. Downloading...")
            nltk.download(package_id)
            print(f"'{package_id}' downloaded successfully.")

class QuestionGenerator:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add marks for each question type including the new deep facility questions
        self.question_marks = {
            "Factual Questions": 1,
            "Analytical Questions": 2,
            "Comprehension Questions": 2,
            "Multiple Choice Questions": 3,
            "Fill in the Blank Questions": 2,
            "Deep Facility Questions": 10  # New question type with 10 marks
        }
        self.question_templates = {
            'what': [
                "What is {}?",
                "What does {} mean?",
                "What are the main characteristics of {}?",
                "What happens when {}?"
            ],
            'who': [
                "Who is {}?",
                "Who was involved in {}?",
                "Who discovered {}?",
                "Who created {}?"
            ],
            'when': [
                "When did {} occur?",
                "When was {} established?",
                "When does {} happen?"
            ],
            'where': [
                "Where is {} located?",
                "Where did {} take place?",
                "Where can {} be found?"
            ],
            'why': [
                "Why is {} important?",
                "Why does {} happen?",
                "Why did {} occur?"
            ],
            'how': [
                "How does {} work?",
                "How is {} created?",
                "How can {} be improved?"
            ]
        }
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases and named entities from text"""
        sentences = sent_tokenize(text)
        key_phrases = []
        
        for sentence in sentences:
            # Tokenize and tag parts of speech
            tokens = word_tokenize(sentence)
            pos_tags = pos_tag(tokens)
            
            # Extract noun phrases
            noun_phrases = []
            current_phrase = []
            
            for word, tag in pos_tags:
                if tag.startswith('N') or tag.startswith('J'):  # Nouns and adjectives
                    current_phrase.append(word)
                else:
                    if current_phrase:
                        phrase = ' '.join(current_phrase)
                        if len(phrase.split()) >= 1 and phrase.lower() not in self.stop_words:
                            noun_phrases.append(phrase)
                        current_phrase = []
            
            # Add remaining phrase
            if current_phrase:
                phrase = ' '.join(current_phrase)
                if len(phrase.split()) >= 1 and phrase.lower() not in self.stop_words:
                    noun_phrases.append(phrase)
            
            key_phrases.extend(noun_phrases)
        
        # Extract named entities
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        chunks = ne_chunk(pos_tags)
        
        named_entities = []
        for chunk in chunks:
            if hasattr(chunk, 'label'):
                entity = ' '.join([token for token, pos in chunk.leaves()])
                named_entities.append(entity)
        
        # Combine and filter
        all_phrases = key_phrases + named_entities
        
        # Remove duplicates and filter by frequency
        phrase_counts = Counter(all_phrases)
        filtered_phrases = [phrase for phrase, count in phrase_counts.items() 
                          if len(phrase.split()) <= 4 and len(phrase) > 2]
        
        return list(set(filtered_phrases))[:10]  # Return top 10 unique phrases
    
    def generate_multiple_choice_questions(self, text: str, key_phrases: List[str]) -> List[Dict]:
        """Generate multiple choice questions with options"""
        sentences = sent_tokenize(text)
        questions = []
        
        # Use key phrases to create questions
        for phrase in key_phrases[:3]:  # Limit to top 3 phrases
            # Find sentences containing the key phrase
            relevant_sentences = [s for s in sentences if phrase.lower() in s.lower()]
            
            if not relevant_sentences:
                continue
                
            # Create question from the first relevant sentence
            sentence = relevant_sentences[0]
            
            # Create question text
            question_text = f"Which of the following best describes {phrase}?"
            
            # Correct answer is the sentence containing the phrase
            correct_answer = sentence
            
            # Generate distractors (incorrect options)
            distractors = []
            for s in sentences:
                if s != sentence and len(s) > 20 and s not in distractors:
                    distractors.append(s)
            
            # If we don't have enough distractors, create some
            while len(distractors) < 3 and len(distractors) < len(sentences) - 1:
                distractor = f"This is not related to {phrase}."
                if distractor not in distractors:
                    distractors.append(distractor)
            
            # Limit distractor length
            distractors = [d[:100] + '...' if len(d) > 100 else d for d in distractors[:3]]
            
            # Create options (shuffle correct answer with distractors)
            options = [correct_answer] + distractors
            random.shuffle(options)
            
            # Find index of correct answer
            correct_index = options.index(correct_answer)
            
            # Add question to list with marks
            questions.append({
                'question': question_text,
                'options': options,
                'correct_answer_index': correct_index,
                'marks': self.question_marks["Multiple Choice Questions"]
            })
        
        return questions
    
    def generate_fill_in_blank_questions(self, text: str, key_phrases: List[str]) -> List[Dict]:
        """Generate fill-in-the-blank questions"""
        sentences = sent_tokenize(text)
        questions = []
        
        # Use sentences containing key phrases
        for phrase in key_phrases[:3]:  # Limit to top 3 phrases
            # Find sentences containing the key phrase
            relevant_sentences = [s for s in sentences if phrase.lower() in s.lower()]
            
            if not relevant_sentences:
                continue
                
            # Use the first relevant sentence
            sentence = relevant_sentences[0]
            
            # Replace the phrase with a blank
            blank_sentence = sentence.replace(phrase, "___________")
            
            # If phrase wasn't found with exact case, try case-insensitive replacement
            if blank_sentence == sentence:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                blank_sentence = pattern.sub("___________", sentence)
            
            # Add question to list with marks
            questions.append({
                'question': blank_sentence,
                'answer': phrase,
                'marks': self.question_marks["Fill in the Blank Questions"]
            })
        
        return questions
    
    def generate_factual_questions(self, text: str, key_phrases: List[str]) -> List[Dict]:
        """Generate factual questions based on key phrases"""
        questions = []
        
        for phrase in key_phrases[:5]:  # Limit to top 5 phrases
            # Choose random question type and template
            question_types = ['what', 'who', 'when', 'where']
            question_type = random.choice(question_types)
            template = random.choice(self.question_templates[question_type])
            
            try:
                question_text = template.format(phrase)
                questions.append({
                    'question': question_text,
                    'marks': self.question_marks["Factual Questions"]
                })
            except:
                continue
        
        return questions
    
    def generate_analytical_questions(self, text: str) -> List[Dict]:
        """Generate analytical and critical thinking questions"""
        analytical_questions = [
            "What are the main arguments presented in this text?",
            "How does this information relate to current events?",
            "What evidence supports the claims made in this passage?",
            "What are the potential implications of the ideas discussed?",
            "How might different perspectives view this topic?",
            "What questions does this text raise that aren't answered?",
            "What are the strengths and weaknesses of the arguments presented?",
            "How could this information be applied in real-world situations?"
        ]
        
        # Return 3-4 random analytical questions with marks
        selected_questions = random.sample(analytical_questions, min(4, len(analytical_questions)))
        return [{'question': q, 'marks': self.question_marks["Analytical Questions"]} for q in selected_questions]
    
    def generate_comprehension_questions(self, text: str) -> List[Dict]:
        """Generate reading comprehension questions"""
        sentences = sent_tokenize(text)
        questions = []
        
        if len(sentences) >= 2:
            for q in ["What is the main idea of this passage?",
                     "Summarize the key points discussed in the text.",
                     "What conclusion can be drawn from this information?"]:
                questions.append({'question': q, 'marks': self.question_marks["Comprehension Questions"]})
        
        if len(sentences) >= 3:
            questions.append({'question': "How do the different parts of this text connect to each other?", 
                             'marks': self.question_marks["Comprehension Questions"]})
        
        return questions
    
    def generate_deep_facility_questions(self, text: str, key_phrases: List[str]) -> List[Dict]:
        """Generate deep facility questions worth 10 marks that test deeper understanding"""
        questions = []
        
        # Deep analytical questions that require comprehensive understanding
        deep_questions = [
            "Critically evaluate the implications of {} on various stakeholders and provide a comprehensive analysis of potential long-term consequences.",
            "Compare and contrast different theoretical frameworks that could be applied to understand {}. Analyze their strengths and limitations in this context.",
            "Develop a detailed proposal addressing the challenges related to {} with consideration of ethical, economic, and social dimensions.",
            "Analyze how {} intersects with broader systems and structures. Evaluate potential interventions and their likely outcomes.",
            "Synthesize multiple perspectives on {} and construct a nuanced argument that acknowledges the complexity of this topic."
        ]
        
        # Use the most significant key phrases for deep questions
        significant_phrases = key_phrases[:2]  # Use top 2 key phrases
        
        for phrase in significant_phrases:
            # Select a random deep question template
            template = random.choice(deep_questions)
            question_text = template.format(phrase)
            
            # Add question to list with 10 marks
            questions.append({
                'question': question_text,
                'marks': self.question_marks["Deep Facility Questions"]
            })
        
        return questions
    
    def generate_questions(self, paragraph: str, num_questions: int = 10) -> Dict[str, List[str]]:
        """Generate various types of questions from a paragraph"""
        if not paragraph or len(paragraph.strip()) < 50:
            return {"error": ["Paragraph is too short. Please provide at least 50 characters."]}
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(paragraph)
        
        # Generate different types of questions
        factual_questions = self.generate_factual_questions(paragraph, key_phrases)
        analytical_questions = self.generate_analytical_questions(paragraph)
        comprehension_questions = self.generate_comprehension_questions(paragraph)
        multiple_choice_questions = self.generate_multiple_choice_questions(paragraph, key_phrases)
        fill_in_blank_questions = self.generate_fill_in_blank_questions(paragraph, key_phrases)
        deep_facility_questions = self.generate_deep_facility_questions(paragraph, key_phrases)  # New question type
        
        # Combine all questions
        all_questions = {
            "Factual Questions": factual_questions,
            "Analytical Questions": analytical_questions,
            "Comprehension Questions": comprehension_questions,
            "Multiple Choice Questions": multiple_choice_questions,
            "Fill in the Blank Questions": fill_in_blank_questions,
            "Deep Facility Questions": deep_facility_questions,  # Add new question type
            "Key Phrases Identified": key_phrases
        }
        
        return all_questions

def main():
    print("🤖 AI Question Generator from Paragraphs")
    print("=" * 50)
    
    generator = QuestionGenerator()
    
    # Sample paragraph for demonstration
    sample_paragraph = """
    Artificial intelligence (AI) is a rapidly evolving field that focuses on creating machines 
    capable of performing tasks that typically require human intelligence. These tasks include 
    learning, reasoning, problem-solving, perception, and language understanding. Machine learning, 
    a subset of AI, enables computers to learn and improve from experience without being explicitly 
    programmed. Deep learning, which uses neural networks with multiple layers, has revolutionized 
    areas such as image recognition, natural language processing, and autonomous vehicles. As AI 
    technology continues to advance, it raises important questions about ethics, job displacement, 
    and the future relationship between humans and machines.
    """
    
    print("Sample paragraph:")
    print("-" * 30)
    print(sample_paragraph.strip())
    print("\n")
    
    # Generate questions
    print("Generating questions...")
    questions = generator.generate_questions(sample_paragraph)
    
    # Display results
    for category, question_list in questions.items():
        print(f"\n📝 {category}:")
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
    
    print("\n" + "=" * 50)
    print("💡 Usage Instructions:")
    print("1. Replace the sample_paragraph variable with your own text")
    print("2. Run the script to generate questions automatically")
    print("3. Customize question templates in the QuestionGenerator class")
    print("4. Adjust the number of questions by modifying the limits in each method")
    print("5. Modify the marks for each question type in the question_marks dictionary")

if __name__ == "__main__":
    main()
