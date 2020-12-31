from random import randint
from human_template import Human
from smith import Smith


class Matrix:
    def __init__(self):
        self._mankind = []
        self.reset_world()
        print("** MATRIX INITIATED **")

    def generate_people(self, population=10):
        for i in range(0, population):
            human = Human()
            self._mankind.append(human)
        print("Generated all people in the world.")

    def get_total_males_females(self):
        males = females = 0
        for actor in self._mankind:
            if actor.gender == Human.GENDER[0]:
                males = males + 1
            elif actor.gender == Human.GENDER[1]:
                females = females + 1

        return males, females

    def action(self):
        """
        This represents time. Humans doing activities
        """
        actor = self._mankind[randint(0, len(self._mankind) - 1)]

        # Decides if this actor will interact with someone else
        will_interact = True if randint(0, 1) == 1 else False
        if will_interact:
            second_actor = actor
            while second_actor == actor:
                second_actor = self._mankind[randint(0, len(self._mankind) - 1)]

            print(
                "A {} interacted with a {}.".format(actor.gender, second_actor.gender)
            )
            actor.live(second_actor)
        else:
            print("A {} interacted with himself/herself.".format(actor.gender))
            actor.live()

    def reset_world(self):
        self._mankind = [Smith()]
