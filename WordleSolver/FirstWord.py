# WordleSolver/main.py
from worldle_word_scraper import compile_prev_answers, find_five_letter_word
from find_words import find_word_from_url
from letter_instances import find_top_letters


def get_filename():
    usr_in = input("Please type filename or prev for a preset name without included extension:")
    
    if usr_in == "prev":
        filename = "extracted_answers.txt"
    else:
        filename = usr_in + ".txt"

    return filename

def main():
    filename = get_filename()
    
    compile_prev_answers(filename)
    wanted_letters = find_top_letters(filename)

    find_word_from_url(wanted_letters)



    

if __name__ == "__main__":
    main()