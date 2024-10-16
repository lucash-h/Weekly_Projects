import string

def find_top_letters(filename):


    alphabet_dict = {letter: 0 for letter in string.ascii_lowercase}

    print(alphabet_dict)


    with open(filename, 'r') as answer_file:
        for line in answer_file:
            for char in line:
                if(char != '\n'):
                    alphabet_dict[char.lower()] += 1

    print(alphabet_dict)

    sorted_alphabet_dict = dict(sorted(alphabet_dict.items(), key=lambda item: item[1], reverse=True))

    print("Sorted dictionary by value:")
    print(sorted_alphabet_dict)

    top5_dict = dict(list(sorted_alphabet_dict.items())[:5])

    print("5 most frequent letters")
    print(top5_dict)

    five_letters = ''.join(top5_dict.keys())

    print("five_letters")
    print(five_letters)

    return five_letters
'''


with open('extracted_answers', 'r') as answer_file:
    for line in answer_file:
        for char in line:
            if char != '\n':
                alphabet_dict[char.lower()] += 1



find_five_letter_words_website = f'https://www.thewordfinder.com/wordlist/words-containing-letters-{five_letters}/?dir=ascending&field=word&pg=1&size=5'
'''

