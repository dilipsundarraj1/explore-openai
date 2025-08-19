"""
OpenAI Response API - Image Input Example
This script demonstrates how to use the OpenAI Response API with image input.
The Response API allows you to send images along with text prompts to analyze visual content.
"""

from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

def analyze_image_from_url():
    """Analyze an image from a URL using the Response API"""
    print("🖼️ Analyzing image from URL...")
    
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",  # or gpt-4.1, gpt-4.1-preview, etc.
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "What's in this picture? Describe it in detail."},
                        {
                            "type": "input_image",
                            "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
                        }
                    ]
                }
            ]
        )
        
        print("Response:")
        print(response.output[0].content[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def analyze_multiple_aspects():
    """Ask multiple questions about the same image"""
    print("\n🔍 Analyzing multiple aspects of the image...")
    
    questions = [
        "What colors do you see in this image?",
        "What is the main subject of this image?",
        "Can you identify any text or logos in the image?",
        "What is the background like?"
    ]
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": question},
                            {
                                "type": "input_image",
                                "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
                            }
                        ]
                    }
                ]
            )
            
            print(f"Answer: {response.output[0].content[0].text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def analyze_different_image():
    """Analyze a different image to show versatility"""
    print("\n🌟 Analyzing a different image...")
    
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Describe this image and identify what programming language or technology this might be related to."},
                        {
                            "type": "input_image",
                            "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg"
                        }
                    ]
                }
            ]
        )
        
        print("Response:")
        print(response.output[0].content[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def complex_image_analysis():
    """Perform complex analysis with specific instructions"""
    print("\n🧠 Complex image analysis with specific instructions...")
    
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text", 
                            "text": """Please analyze this image and provide:
                            1. A brief description of what you see
                            2. The dominant colors
                            3. Any geometric shapes or patterns
                            4. The overall composition and layout
                            5. What this image might be used for
                            
                            Format your response with clear headings for each point."""
                        },
                        {
                            "type": "input_image",
                            "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
                        }
                    ]
                }
            ]
        )
        
        print("Detailed Analysis:")
        print(response.output[0].content[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 OpenAI Response API - Image Input Examples")
    print("=" * 50)
    
    # Run different examples
    analyze_image_from_url()
    analyze_multiple_aspects()
    analyze_different_image()
    complex_image_analysis()
    
    print("\n✅ Image analysis examples completed!")
