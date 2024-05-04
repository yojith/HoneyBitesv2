from openai import OpenAI

def initialize():
    with open("OpenAI_key.txt", "r") as file:
        chatgpt_api_key = file.read().strip()
        client = OpenAI(api_key=chatgpt_api_key)
    return client

def get_input():
    input_text = "Hi"
    return input_text

def categorize(client, system_prompt:str, input_text: str):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=1
    )
    return (response.choices[0].message.content, response.usage)


def sort_cuisine(client, food):
    '''
    Takes one food and returns one cuisine
    '''
    cuisines_list = ['Chinese', 'Korean', 'Japanese', 'Vietnamese', 'Thai', 'Indian', 'Philipino', 'Middle Eastern', 'Greek', 'Italian', 'French', 'British', 'German', 'Polish', 'Russian', 'Spanish', 'Scandinavian', 'African', 'Carribean', 'American', 'Brazilian', 'Latin American', 'Mexican']
    cuisines = ','.join(cuisines_list)
    system_prompt = f"{cuisines}. Those a list of types of cuisines. From this list, which categories fits best? Please only return one, if none, return None"
    transcript_text = food
    output = categorize(client, system_prompt, transcript_text)
    cuisine = output[0]

    return cuisine
    


if __name__ == "__main__":
    client = initialize()
    output = sort_cuisine("Takoyaki")
    print(output)

    category = output[0]