import json
import random
import textwrap

import npyscreen
from npyscreen import wgwidget as widget
from npyscreen.utilNotify import notify_confirm

QUIZ_JSON_FILE = 'quiz.json'
SCREEN_WIDTH = 70  # give a little additional space around the edges of the console window
HIGHLIGHT_OK_BUTTON = 1


class ActionFormWithConfirmButton(npyscreen.ActionFormMinimal):
    OK_BUTTON_TEXT = 'Confirm'


# noinspection PyAttributeOutsideInit
class QuizForm(ActionFormWithConfirmButton):
    def create(self):
        """ Override for performing form creation """
        with open(QUIZ_JSON_FILE) as quiz_file:
            self.json_data = json.load(quiz_file)
        self.categories = list(self.json_data.keys())
        self.correct_term = None
        self.num_correct_answers = 0
        self.num_questions_asked = 0
        self.exiting = False  # set to True when app is closing
        self.data = self.transform_json_data()
        random.shuffle(self.data)

        # UI controls for console window
        self.lbl_score = self.add(npyscreen.TitleFixedText, name='Score:', value='0 / 0', editable=False)
        self.lbl_category = self.add(npyscreen.TitleFixedText, name='Category:', editable=False)
        definition_text = 'Definition: '
        self.definition_width = SCREEN_WIDTH - len(definition_text)
        self.lbl_definition = self.add(npyscreen.MultiLineEditableTitle, name=definition_text, max_height=5,
                                       editable=False)
        self.opt_terms = self.add(npyscreen.TitleSelectOne, name='Pick One', scroll_exit=True)

    def set_up_exit_condition_handlers(self):
        """ Override for custom exit event handlers """
        super(ActionFormWithConfirmButton, self).set_up_exit_condition_handlers()
        self.how_exited_handers.update({
            widget.EXITED_ESCAPE:   self.exit_app
        })

    def exit_app(self):
        """ Method to shut down NPSApp gracefully """
        self.exiting = True
        self.parentApp.switchForm(None)

    # noinspection PyAttributeOutsideInit
    def transform_json_data(self):
        """ JSON data is stored as nested dictionaries to save space. Here it's turned into a
        list of tuples with the category and term keys joined together.
        :return: list of tuples [('cat1:term1', defn1), (cat1:term2), defn2], (cat2:term3), defn3), ...] """
        new_data = []
        for category in self.categories:
            category_terms_and_definitions = self.json_data[category]
            for term, definition in category_terms_and_definitions.items():
                key = '{0}:{1}'.format(category, term)
                new_data.append((key, definition))
        return new_data

    def find_other_possible_terms(self, category):
        """
        :param: category -- category name
        :return: list of terms that belong to the category
        """
        category_prefix = '{}:'.format(category)
        possible_terms = []
        for other_term, _ in self.data:
            if other_term.startswith(category_prefix):
                _, other_term = other_term.split(':')
                possible_terms.append(other_term)
        return possible_terms

    def update_score(self):
        """ Updates the score in the score label. """
        self.lbl_score.value = '{} / {}'.format(self.num_correct_answers, self.num_questions_asked)

    def get_score(self):
        """ Returns a score string intended for display once the program exits."""
        if self.data:
            return 'Your score up to this point was {} out of {}.'.format(self.num_correct_answers,
                                                                          self.num_questions_asked)
        else:
            return 'Your final score was {} out of {}.'.format(self.num_correct_answers, self.num_questions_asked)

    def get_another_question(self):
        """ Pops a question off the data list and passes the items back, or None if no questions remain. """
        while self.data:
            category_and_term, definition = self.data.pop()
            category, term = category_and_term.split(':')
            other_possible_terms = self.find_other_possible_terms(category)
            if other_possible_terms:
                return category, definition, term, other_possible_terms
        return None

    def ask(self, question):
        """ Populate the fields on the main form with the current score and the question asked: the definition and
        the potential terms. The correct term is stored as a variable, and it's used to assess whether the user got
        the question right in the on_ok method.
        :param: question - tuple consisting of (category, definition, term, other_possible_terms)
        :return: None """
        category, definition, term, other_possible_terms = question
        self.update_score()
        self.lbl_category.value = category
        self.lbl_definition.values = textwrap.wrap(definition, self.definition_width)
        all_terms = [term] + other_possible_terms
        random.shuffle(all_terms)
        self.opt_terms.value = None
        self.opt_terms.values = all_terms
        self.opt_terms.entry_widget.reset_cursor()  # puts cursor back at the top of the list
        self.correct_term = term
        self.num_questions_asked += 1

    # TRICKY: Events on a form are fired in this sequence:
    # 1. beforeEditing (when widgets have been created or updated)
    # 2. edit (when widgets on the form are responding to user input)
    # 3. on_ok/on_cancel (when the user clicks the OK or Cancel button on the form)
    # 4. afterEditing (when all other form events are complete)
    #
    # The event firing sequence cannot be interrupted, which is unusual for a UI framework.
    #
    # To adapt to this, I ask the first question in beforeEditing (triggered once when the widgets are created),
    # and ask all remaining questions in afterEditing. It's the equivalent of a loop and a half pattern
    # spread across two separate event functions. 
    # (See https://users.cs.duke.edu/~ola/patterns/plopd/loops.html#loop-and-a-half)
    def beforeEditing(self):
        if self.num_questions_asked == 0:
            question = self.get_another_question()
            if question:
                self.ask(question)

    def afterEditing(self):
        if not self.exiting:
            question = self.get_another_question()
            if question:
                self.ask(question)
            else:
                self.exit_app()

    def on_ok(self):
        if self.correct_term in self.opt_terms.get_selected_objects():
            self.num_correct_answers += 1
        else:
            # The default behavior for notify_confirm is NOT to highlight the OK button. What the ... ?
            notify_confirm("I'm sorry; the correct answer was {}.".format(self.correct_term), "Incorrect answer",
                           "STANDOUT", True, False, HIGHLIGHT_OK_BUTTON)


class QuizTakerConsoleApp(npyscreen.NPSAppManaged):
    """ Simple app that just uses one form. """
    def onStart(self):
        self.addForm('MAIN', QuizForm)


if __name__ == '__main__':
    app = QuizTakerConsoleApp()
    app.run()  # start main loop
    # once the app exits (either normally or using the ESC key), print the score for the user.
    main_form = app.getForm('MAIN')
    print(main_form.get_score())
