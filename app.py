import chainlit as cl
import requests
import json
from typing import List, Tuple
from cast_of_characters import characters, Character
from story import story_opening

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

conversation_context: List[str] = []

# Constants 
LMSTUDIO_API_URL = "http://localhost:1234/v1/completions"
MAX_CONTEXT_MESSAGES = 10
MAX_TOKENS = 4096

def get_character_from_message(message: str) -> Tuple[Character, str]:
    for char_name in characters.keys():
        if f"@{char_name}" in message.lower():
            return characters[char_name], message.replace(f"@{char_name}", "").strip()
    return characters["Narrator"], message.strip()

def analyze_user_message(message: str) -> str:
 
    sia = SentimentIntensityAnalyzer()
    
    sentiment_scores = sia.polarity_scores(message)

    if sentiment_scores['compound'] >= 0.05:
        sentiment_label = "positive"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    print(f"User message sentiment: {sentiment_label} (score: {sentiment_scores['compound']})")

    words = word_tokenize(message)
    word_count = len(words)
    print(f"User message word count: {word_count}")
    
    return message

def analyze_generated_text(text: str) -> str:

    sia = SentimentIntensityAnalyzer()

    sentiment_scores = sia.polarity_scores(text)

    if sentiment_scores['compound'] >= 0.05:
        sentiment_label = "positive"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"
    
    # Log the sentiment analysis (optional: can be used for debugging)
    print(f"Generated text sentiment: {sentiment_label} (score: {sentiment_scores['compound']})")
    
    # Count words using NLTK word_tokenize
    words = word_tokenize(text)
    word_count = len(words)
    print(f"Generated text word count: {word_count}")
    
    return text

def process_generated_text(text: str) -> str:
    sia = SentimentIntensityAnalyzer()

    sentiment_scores = sia.polarity_scores(text)
    
    if sentiment_scores['compound'] >= 0.05:
        sentiment_label = "positive"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    print(f"Processed text sentiment: {sentiment_label} (score: {sentiment_scores['compound']})")

    words = word_tokenize(text)
    word_count = len(words)
    print(f"Processed text word count: {word_count}")
    
    return text

@cl.on_chat_start
async def start():
    """Initialize chat with story opening"""
    msg = cl.Message(content=story_opening)
    await msg.send()
    conversation_context.append(f"Narrator: {story_opening}")

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    try:
        # 1. Analyze user message (STUDENT CODE CAN BE USED HERE WITH THIS FUNCTION)
        analyzed_message = analyze_user_message(message.content)
        
        # 2. Get character and clean message
        character, clean_message = get_character_from_message(analyzed_message)
        
        # 3. Add user message to context
        conversation_context.append(f"User: {clean_message}")
        
        # 4. Construct full prompt with system prompt and conversation history
        full_prompt = f"""System Prompt: {character.role}

Conversation History:
{chr(10).join(conversation_context[-MAX_CONTEXT_MESSAGES:])}

{character.name}:"""

        # Prepare API payload
        payload = {
            "model": "mistral-7b-instruct-v0.3",
            "prompt": full_prompt,
            "temperature": 0.7,
            "stream": True,
            "max_tokens": 1024
        }

        # Send request to LM Studio's API
        msg.content = f"@{character.name} "
        await msg.update()
        
        response = requests.post(LMSTUDIO_API_URL, json=payload, stream=True)
        response.raise_for_status()

        accumulated_response = ""
        
        # Process streaming response
        first_token = True  # Track if it's the first token
        for line in response.iter_lines():
            if line:
                try:
                    clean_line = line.decode("utf-8").strip()
                    if clean_line.startswith("data: "):
                        clean_line = clean_line[6:].strip()
                    
                    if clean_line == "[DONE]":
                        break

                    decoded_line = json.loads(clean_line)
                    text_part = decoded_line.get("choices", [{}])[0].get("text", "")

                    if "User" in text_part:
                        break

                    if text_part:
                        # Option to Process text tokens in real-time
                        # STUDENT EXERCISE: Add token-level processing here
                        accumulated_response += text_part
                        await msg.stream_token(text_part)

                except json.JSONDecodeError:
                    continue

        # Process complete response
        if accumulated_response.strip():
            
            analyzed_message = analyze_generated_text(accumulated_response.strip())
            processed_response = process_generated_text(analyzed_message)
            

            conversation_context.append(f"{character.name}: {processed_response}")
            await msg.send()
        else:
            await cl.Message(content="Sorry, I couldn't generate a response.").send()

    except requests.RequestException as e:
        error_msg = f"Error communicating with LM Studio: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()

        await cl.Message(content=error_msg).send()

#PIG LATIN SECTION BY BRYTON
VOWELS = "aeiouAEIOU"


def to_pig_latin_word(word: str) -> str:
    """Convert a single word to Pig Latin."""
    # Preserve punctuation at the end
    suffix = ""
    while word and not word[-1].isalpha():
        suffix = word[-1] + suffix
        word = word[:-1]

    if not word or not word[0].isalpha():
        return word + suffix

    is_capitalized = word[0].isupper()
    lower = word.lower()

    if lower[0] in VOWELS:
        pig = lower + "yay"
    else:
        # Find the first vowel
        first_vowel = next((i for i, c in enumerate(lower) if c in VOWELS), None)
        if first_vowel is None:
            pig = lower + "ay"
        else:
            pig = lower[first_vowel:] + lower[:first_vowel] + "ay"

    if is_capitalized:
        pig = pig.capitalize()

    return pig + suffix


def to_pig_latin(text: str) -> str:
    """
    Convert a full text string to Pig Latin using NLTK tokenization.
    Appends the original text in parentheses at the end.
    """
    tokens = word_tokenize(text)

    pig_tokens = []
    for token in tokens:
        pig_tokens.append(to_pig_latin_word(token))

    pig_text = " ".join(pig_tokens)

    return f"{pig_text} ({text})"
    # Check if character is the Butcher
if Character == 'Butcher':
    processed_response = to_pig_latin(processed_response)
    # Add the processed response to the context
    conversation_context.append(processed_response)  

# The session continues and other characters are processed accordingly
await msg.send()
