
from random import randint, random, uniform
from keyboard import write, press
from time import sleep
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

from typing import Dict, List, Tuple, Union
import collections
import itertools
import textwrap

class Keyboard(collections.UserDict):
    """"""
    @property
    def n_rows(self):
        return int(max(pos.real for pos in self.values()) + 1)

    @property
    def n_columns(self):
        return int(max(pos.imag for pos in self.values()) + 1)

    @property
    def shape(self):
        return (self.n_rows, self.n_columns)

    def char_distance(self, c1: str, c2: str) -> float:
        """Euclidean distance between two characters."""
        return abs(self[c1] - self[c2]) if c1 != c2 else 0.0


    def typing_distance(self, word: str) -> float:
        return sum(self.char_distance(c1, c2) for c1, c2 in zip(word, word[1:]))

    @classmethod
    def from_coordinates(
        cls,
        coordinates: Dict[str, Tuple[int, int]],
        staggering: Union[float, List] = 0,
        horizontal_pitch=1,
        vertical_pitch=1,
    ):
        """
        Parameters
        ----------
        coordinates
            A dictionary specifying the (row, col) location of each character. The origin is
            assumed to be at the top-left corner.
        staggering
            Controls the amount of staggering between consecutive rows. The amount of staggering is
            the same between pair of consecutive rows if a single number is specified. Variable
            amounts of staggering can be specified by providing a list of length `n_rows - 1`,
            within which the ith element corresponds the staggering between rows `i` and `i + 1`.
        horizontal_pitch
            The horizontal distance between the center of two adjacent keys.
        vertical_pitch
            The vertical distance between the center of two adjacent keys.
        """
        if isinstance(staggering, list):
            staggering = list(itertools.accumulate(staggering, initial=0))

        return cls(
            {
                char: complex(
                    i * vertical_pitch,
                    j * horizontal_pitch
                    + (
                        staggering[i]
                        if isinstance(staggering, list)
                        else i * staggering
                    ),
                )
                for char, (i, j) in coordinates.items()
            }
        )

    @classmethod
    def from_grid(
        cls,
        grid: str,
        staggering: Union[float, List] = 0,
        horizontal_pitch=1,
        vertical_pitch=1,
    ):
        """
        Parameters
        ----------
        grid
            A keyboard layout specified as a grid separated by spaces. See the examples to
            understand the format.
        staggering
            Controls the amount of staggering between consecutive rows. The amount of staggering is
            the same between pair of consecutive rows if a single number is specified. Variable
            amounts of staggering can be specified by providing a list of length `n_rows - 1`,
            within which the ith element corresponds the staggering between rows `i` and `i + 1`.
        horizontal_pitch
            The horizontal distance between the center of two adjacent keys.
        vertical_pitch
            The vertical distance between the center of two adjacent keys.
        """
        return cls.from_coordinates(
            coordinates={
                char: (i, j)
                for i, row in enumerate(filter(len, textwrap.dedent(grid).splitlines()))
                for j, char in enumerate(row[::2])
                if char
            },
            staggering=staggering,
            horizontal_pitch=horizontal_pitch,
            vertical_pitch=vertical_pitch,
        )

    def __repr__(self):
        rows = [[] for _ in range(self.n_rows)]
        reverse_layout = {
            (int(pos.real), int(pos.imag)): char for char, pos in self.items()
        }
        for i, j in sorted(reverse_layout.keys()):
            rows[i].extend([" "] * (j - len(rows[i])))
            rows[i].append(reverse_layout[i, j])
        return "\n".join(" ".join(row) for row in rows)





class Human_typer():
    """
    Class for the Human like typer
    
    :Args: 
        - keyboard_layout : str = "qwerty" or "azerty" (default:qwerty)
        - average_cpm : float (default:190 (Median CPM))
    
    Example :
    ```python
    My_Typer = Human_typer("azerty", 70)
    ```
    """
    def __init__(self, keyboard_layout : str = "qwerty", average_wpm : float = 190) -> None:
        self.cpm_range = (round(60/(3.2*average_wpm),3), round(60/(0.8*average_wpm),3))
        print(self.cpm_range)
        self.qwerty_min= Keyboard.from_grid(
            """
            ` 1 2 3 4 5 6 7 8 9 0 - =
            q w e r t y u i o p [ ] \\
            a s d f g h j k l ; '
            z x c v b n m , . /
            """)

        self.qwerty_maj = Keyboard.from_grid(
            """
            ~ ! @ # $ % ^ & * ( ) _ +
            Q W E R T Y U I O P { } |
            A S D F G H J K L : "
            Z X C V B N M < > ?
            """
        )

        self.azerty_min = Keyboard.from_grid(
            """
            ² & é " ' ( - è _ ç à ) =
            a z e r t y u i o p ^ $
            q s d f g h j k l m ù *
            w x c v b n , ; : !
            """
        )

        self.azerty_maj = Keyboard.from_grid(
            """
            1 2 3 4 5 6 7 8 9 0 ° +
            A Z E R T Y U I O P ¨ £
            Q S D F G H J K L M % µ
            W X C V B N ? . / §
            """
        )

        self.azerty_alt = Keyboard.from_grid(
            """
            ~ # { [ | ` \\ ^ @ ] }
            €                  ¤
            """
        )
        self.all_qwerty = [self.qwerty_min, self.qwerty_maj]
        self.all_azerty = [self.azerty_min, self.azerty_maj, self.azerty_alt]
        
        if keyboard_layout == "qwerty":
            self.keyboard_layout = self.all_qwerty
        elif keyboard_layout == "azerty":
            self.keyboard_layout = self.all_azerty
    
    
    def get_random_close_neighbor(self, letter : str, letter_layout_type : Keyboard) -> list:
        """Get the close neighbors of the given letter in the adapted keyboard layout"""
        distance_list, item_list = [], []
        for car in letter_layout_type:
            if car != letter:
                distance_list.append(Keyboard.char_distance(letter_layout_type, car, letter))
                item_list.append(car)
        return [i[1] for i in sorted(zip(distance_list, item_list), reverse=False)[:3]][randint(0,2)]
        
    def find_layout(self, car : str) -> Keyboard:
        """Find the adapted keyboard layout for the given caracter"""
        for layout_type in self.keyboard_layout:
            if car in layout_type.data.keys():
                return layout_type
    
    def make_voluntary_error(self, text : str) -> str and list:
        """Generate errors in the given text"""
        number_of_errors = round(len(text) * 0.02 * randint(1, 10))
        errors_index_list, modification_list = [], []
        for _ in range(number_of_errors):
            errors_index_list.append(randint(0, len(text) - 1))
        for index in errors_index_list:
            if text[index] != " ":
                if random() > 0.3:
                    modified_letter = self.get_random_close_neighbor(text[index], self.find_layout(text[index]))
                    modification_list.append([index, text[index], modified_letter, "MODIFY"])
                    text = text[:index] + modified_letter + text[index + 1:]
                else:
                    modified_letter = self.get_random_close_neighbor(text[index], self.find_layout(text[index]))
                    modification_list.append([index, text[index], modified_letter, "ADD"])
                    text = text[:index + 1] + modified_letter + text[index + 1:]     
        return text, modification_list
        
        
    def keyboard_type(self, text : str) -> None:
        """
        Type the text like a human, directly simulating the keyboard
        
        :Args:
            - text - Text to type like a human

        :Usage:
        ```
        keyboard_type("An example text to write human-likely")
        ```

        :rtype: None
        """
        new_text, modification_list = self.make_voluntary_error(text)
        index_to_look_at, index_to_look_at_type = [], []
        for elem in modification_list:
            index_to_look_at.append(elem[0])
            index_to_look_at_type.append(elem[3])
        for index in range(len(text)):
            if index in index_to_look_at:
                if index_to_look_at_type[index_to_look_at.index(index)] == "MODIFY":
                    write(new_text[index])
                    sleep(uniform(0.4,0.5))
                    press("backspace")
                    sleep(uniform(0.4,0.45))
                    write(text[index])
            
                elif index_to_look_at_type[index_to_look_at.index(index)] == "ADD":
                    print(index, text[index], new_text[index])
                    write(text[index])
                    sleep(uniform(self.cpm_range[0], self.cpm_range[1]))
                    write(new_text[index])
                    sleep(uniform(0.4,0.5))
                    press("backspace")
            else:
                write(text[index])

            sleep(uniform(self.cpm_range[0], self.cpm_range[1]))

    def type_in_element(self, text : str, element : WebElement) -> None:
        """
        Type the text given in the element given like an human
        
        :Args:
            - text - Text to type like a human
            - element - Selenium element to type the text into

        :Usage:
        ```
        element = driver.find_element_by_ID(element_id)
        type_in_element(my_text, element)
        ```

        :rtype: None
        """
        new_text, modification_list = self.make_voluntary_error(text)
        index_to_look_at, index_to_look_at_type = [], []
        for elem in modification_list:
            index_to_look_at.append(elem[0])
            index_to_look_at_type.append(elem[3])
        for index in range(len(text)):
            if index in index_to_look_at:
                if index_to_look_at_type[index_to_look_at.index(index)] == "MODIFY":
                    element.send_keys(new_text[index])
                    sleep(uniform(0.4,0.5))
                    element.send_keys(Keys.BACKSPACE)
                    sleep(uniform(0.4,0.45))
                    element.send_keys(text[index])
            
                elif index_to_look_at_type[index_to_look_at.index(index)] == "ADD":
                    print(index, text[index], new_text[index])
                    element.send_keys(text[index])
                    sleep(uniform(self.cpm_range[0], self.cpm_range[1]))
                    element.send_keys(new_text[index])
                    sleep(uniform(0.4,0.5))
                    element.send_keys(Keys.BACKSPACE)
            else:
                element.send_keys(text[index])

            sleep(uniform(self.cpm_range[0], self.cpm_range[1]))
