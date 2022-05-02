import streamlit as st
import pandas as pd
import numpy as np
from game import wordle_game, get_allowed_guesses, select_word
from random import choice

ALLOWED_GUESSES = 6

words = pd.read_csv('unigram_freq.csv')
common_words = list(words.loc[(words['count']>=1000000)].astype(str).word.values)
english_5chars_words = [i.upper() for i in common_words if len(i) == 5]
	
def main():

	target_word = select_word()
	st.write(target_word)
		
	st.markdown("<h1 style='text-align: center; color: #000077;'>WELCOME TO WORDLE</h1>", unsafe_allow_html=True)
	
	wordle_game(target_word)
			
if __name__ == "__main__":
    main()
