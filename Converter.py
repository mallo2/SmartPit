class DataConverter:
    """
    FR : Classe de convertisseur de données\n
    EN : Data converter class
    """
    @staticmethod
    def format_lap_time(lap_time: float) -> str:
        """
        FR : Méthode convertisseur d'un chrono de float à string\n
        EN : Method to convert a float lap time to a string
        :param lap_time: (float)
            FR : Temps du tour
            EN : Lap time
        :return:
            FR : Temps du tour formaté
            EN : Formatted lap time
        """
        return f"{int(lap_time / 60)}:{lap_time % 60:.3f}"

    @staticmethod
    def int_to_pourcentage(i: int) -> str:
        """
        FR : Méthode convertisseur d'un entier à un pourcentage\n
        EN : Method to convert an integer to a percentage
        :param i: (int)
            FR : Entier à transformer
            EN : Integer to transform
        :return:
            FR : Pourcentage formaté
            EN : Formatted percentage
        """
        return f"{i}%"

    @staticmethod
    def int_to_liters(i: int) -> str:
        """
        FR : Méthode convertisseur d'un chrono de float à un volume\n
        EN : Method to convert an integer to a volume
        :param i: (int)
            FR : Volume en litres
            EN : Volume in liters
        :return: (str)
            FR : Volume formaté
            EN : Formatted volume
        """
        return f"{i}L"

    @staticmethod
    def int_to_laps_number(i: int) -> str:
        """
        FR : Méthode convertisseur d'un entier à un nombre de tours\n
        EN : Method to convert an integer to a number of laps
        :param i: (int)
            FR : Nombre de tours
            EN : Number of laps
        :return: (str)
            FR : Nombre de tours formaté
            EN : Formatted number of laps
        """
        return f"{i} tours"