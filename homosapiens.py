class HomoSapiensInterface:
    @property
    def gender(self):
        raise NotImplementedError(
            "This method should be implemented in children classes."
        )

    def live(self):
        raise NotImplementedError(
            "This method should be implemented in children classes."
        )