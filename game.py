import pandas as pd
import streamlit as st
from random import choice
from streamlit_autorefresh import st_autorefresh


TILES = {'correct_place': '#228b22', 'correct_letter': '#FFD700',
         'incorrect': 'grey'}
ALLOWED_GUESSES = 6

words = pd.read_csv('unigram_freq.csv')
common_words = list(words.loc[words['count']
                    >= 1000000].astype(str).word.values)
english_5chars_words = [i.upper() for i in common_words if len(i) == 5]


def select_word(new_word=False):
	if 'target_word' not in st.session_state or new_word:
		target_word = choice(english_5chars_words).upper()
		st.session_state.target_word = target_word
	elif 'target_word' in st.session_state and not new_word:
		target_word = st.session_state.target_word 	
	
	return target_word
	
def validate_guess(guess, answer):
    guessed = []
    tile_pattern = []

    # Loop through every letter of the guess

    for (i, letter) in enumerate(guess):

        # If the letter is in the correct spot, color it in green and add the green tile

        if answer[i] == guess[i]:
            tile_pattern.append(TILES['correct_place'])
            answer = answer.replace(letter, '-', 1)
        elif letter in answer:
            tile_pattern.append(TILES['correct_letter'])
            answer = answer.replace(letter, '-', 1)
        else:

        # Otherwise, the letter doens't exist, just add the grey tile

            guessed += letter
            tile_pattern.append(TILES['incorrect'])

    # Return the joined colored letters and tiles pattern

    return (''.join(guessed), tile_pattern)


def get_allowed_guesses(new_word=False, increment=False):

    if 'allowed_guesses' not in st.session_state:
        st.session_state.allowed_guesses = ALLOWED_GUESSES
    elif 'allowed_guesses' in st.session_state and not new_word and not increment:
        st.session_state.allowed_guesses = \
            st.session_state.allowed_guesses - 1
    elif increment:
        st.session_state.allowed_guesses = \
            st.session_state.allowed_guesses + 1
    elif new_word:
        st.session_state.allowed_guesses = \
            ALLOWED_GUESSES + 2
    

    allowed_guesses = st.session_state.allowed_guesses

    return allowed_guesses


def wordle_game(target):

    GAME_ENDED = False
    if 'history_guesses' not in st.session_state:
        st.session_state.history_guesses = []
    if 'tiles_patterns' not in st.session_state:
        st.session_state.tiles_patterns = []
    if 'colored_guessed' not in st.session_state:
        st.session_state.colored_guessed = []

    # Declare a form and call methods directly on the returned object

    (col1, col2, col3) = st.columns(3)
    new_word = col1.button('Generate a new word')
    if new_word:
        target_word = select_word(new_word=True)
        allowed_guesses = get_allowed_guesses(new_word=True)
        st.markdown('''<h4 style='text-align: center; color: #5F9EA0;'>🎲A new word has been generated</h4>''',
        unsafe_allow_html=True)
        st_autorefresh(interval=0.01 * 60 * 1000, key="dataframerefresh")
        
    hint = col2.button('Get a hint')
    if hint:
        letter = choice(target)
        st.markdown('''<h4 style='text-align: center; color: #DB7093;'>🔎HINT: The word contains the letter {}</h4>'''.format(letter),
                    unsafe_allow_html=True)
        allowed_guesses = get_allowed_guesses(increment=True)
    solution = col3.button('Find out the solution')
    if solution:
        letter = choice(target)
        st.markdown('''<h4 style='text-align: center; color: ##4682B4;'>👉The secret word is {}</h4>'''.format(target),
                    unsafe_allow_html=True)
        guess = 'no try'
        GAME_ENDED = True

    # Keep playing until the user runs out of tries or finds the word

    if not GAME_ENDED:
        allowed_guesses = get_allowed_guesses()
        #st.write('guesses', allowed_guesses)
        if allowed_guesses > 0 and allowed_guesses < ALLOWED_GUESSES+1:
            st.markdown('''<h2 style='text-align: center; color: #0000b2;'>Now guess! You have {} tries</h2>'''.format(allowed_guesses),
                        unsafe_allow_html=True)

        form = st.form(key='first', clear_on_submit=True)
        guess = form.text_input(label='Enter your guess').upper()
        submit = form.form_submit_button(label='Submit')

        BAD_GUESS = True

        # Check the user's guess

        if submit:
            if BAD_GUESS:
                allowed_guesses = st.session_state.allowed_guesses + 1

                # If the guess was already used

                if guess in st.session_state.history_guesses and guess \
                    != None:
                    st.write("You've already guessed this word!!\n")
                elif len(guess) != 5:

                    # guess = st.text_input("Your guess", key='second try').upper()
                # If the guess has not 5 letters

                    st.write('Please enter a 5-letter word!!\n')
                elif guess not in english_5chars_words:

                # If the guess is not in the dictionary

                    st.write('This word does not exist!')
                else:
                    BAD_GUESS = False

        # Append the valid guess

        st.session_state.history_guesses.append(guess)

        # Validate the guess

        (guessed, pattern) = validate_guess(guess, target)

        # Append the results

        st.session_state.colored_guessed.append(guessed)
        st.session_state.tiles_patterns.append(pattern)
        for row in range(len(st.session_state.history_guesses)):
            cols = st.columns(7)
            columns = [cols[1], cols[2], cols[3], cols[4], cols[5]]
            guess = st.session_state.history_guesses[row]
            pattern = st.session_state.tiles_patterns[row]
            for (g, p, col) in zip(guess, pattern, columns):
                col.markdown('''<p style="background-color:{}; text-align: center">{}</p>'''.format(p,
                             g), unsafe_allow_html=True)
        # If the guess is the target or if the user ran out of tries, end the game

        if guess == target or len(st.session_state.history_guesses) \
            == ALLOWED_GUESSES + 1:
            GAME_ENDED = True

    # Print the results

    if GAME_ENDED:
        if guess == 'no try':
            st.markdown("<h2 style='text-align: center; color: #0000b2;'>Play again!</h2>"
                        , unsafe_allow_html=True)
        elif guess != target:
	    st.snow()
            st.markdown("<h2 style='text-align: center; color: #0000b2;'>Dang it! You ran out of tries</h2>"
                        , unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #0000b2;'>The correct word was {}</h3>".format(target),
                        unsafe_allow_html=True)

        elif guess == target:
	    st.balloons()
            st.markdown("""<h2 style='text-align: center; color: #0000b2;'>🏆 You won! 🏆""", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #0000b2;'>You nailed it in {}/{} tries</h3>".format(len(st.session_state.history_guesses),
                        ALLOWED_GUESSES), unsafe_allow_html=True)
