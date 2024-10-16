import webbrowser
import requests
from bs4 import BeautifulSoup as BS

#gets a list of all previous wordle answers and writes them in given filename

def compile_prev_answers(filename):

    past_answers_website = 'https://www.rockpapershotgun.com/wordle-past-answers'

    #webbrowser.open(past_answers_website)

    response = requests.get(past_answers_website)

    if response.status_code == 200:
        soup = BS(response.content, 'html.parser')
        with open(filename, 'w') as answer_file:

            for ultag in soup.find_all('ul', {'class': 'inline'}):
                for litag in ultag.find_all('li'):
                    print(litag.text)
                    answer_file.write(litag.text + '\n')

    else:
        print(f"failed to retrieve website/issue with request message given{response.status_code}")

#uses preset url and 5 letter string to find the first given word from a word finder that has those five letters

def find_five_letter_word(five_letters):

    find_five_letter_words_website = f'https://www.thewordfinder.com/wordlist/words-containing-letters-{five_letters}/?dir=ascending&field=word&pg=1&size=5'
    response = requests.get(find_five_letter_words_website)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse 
        soup = BeautifulSoup(response.content, 'html.parser')
        
        span_elements = soup.find_all('span', class_='letter-class')  # Replace 'letter-class' with the actual class name
        
        word = ''.join([span.text for span in span_elements])
        
        print(f"Extracted word: {word}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


'''
 html = """<ul class='my_class'>
... <li>thing one</li>
... <li>thing two</li>
... </ul>"""
>>> from bs4 import BeautifulSoup as BS
>>> soup = BS(html)
>>> for ultag in soup.find_all('ul', {'class': 'my_class'}):
...     for litag in ultag.find_all('li'):
...             print litag.text
... 
thing one
thing two
'''
