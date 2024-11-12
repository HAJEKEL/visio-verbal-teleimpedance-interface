model="gpt-4o" # Context window is 128000 tokens
response['usage']['total_tokens'] # gives the amount of tokens used in the api call input tokens + output tokens

#Image size
#resizing
"detail": "low"  # resize to 512x512px 
"detail": "high" # resize to less than 768x2000px   

"detail": "low"  # 512x512px budget of 85 tokens
"detail": "high" # 512x512px of whole image and 512x512px of the most important parts of the image budget of 256 tokens
"detail": "auto"

# Explanation of the token counter for images
# https://medium.com/@teekaifeng/gpt4o-visual-tokenizer-an-illustration-c69695dd4a39
