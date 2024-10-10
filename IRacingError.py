class IRacingError(Exception):
    """
    FR : Exception personnalisée pour les erreurs liées à la classe IRacing\n
    EN : Custom exception for errors related to the IRacing class
    """
    def __init__(self, message):
        """
        FR : Constructeur de la classe\n
        EN : Constructor of the class
        :param message:
            FR : Message d'erreur
            EN : Error message
        """
        self.message = message
        super().__init__(self.message)
