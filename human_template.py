from random import randint


class Human:
    NAME = ["John Doe", "Jane Doe"]
    GENDER = ["male", "female"]
    ETHNIC = ["white", "black", "yellow", "multiracial"]
    HEIGHT = [130, 200]

    def __init__(self):
        name = randint(0, len(self.NAME) - 1)
        # Strictly private, can't be changed
        self.__name = self.NAME[name]
        self.__gender = self.GENDER[name]
        self.__ethnic = self.ETHNIC[randint(0, len(self.ETHNIC) - 1)]
        self.__height = randint(self.HEIGHT[0], self.HEIGHT[1])

    def live(self, human=None):
        """
        Usual human activity. Can interact with other humans or not
        """
        pass

    @property
    def gender(self):
        return self.__gender

    def __str__(self):
        can_infect = "Yes" if "infect" in dir(self) else "No"
        return "** HUMAN RESUME **\nName: {}\nGender: {}\nEthnic group: {}\nHeight: {}cm\nCan infect other human? {}".format(
            self.__name, self.__gender, self.__ethnic, self.__height, can_infect
        )
