import irsdk
from asyncio import sleep
from Converter import DataConverter
from IRacingError import IRacingError


class IRacing:
    """
    FR : Classe permettant de récupérer les informations du jeu IRacing\n
    EN : Class to get the information of the IRacing game
    """

    def __init__(self):
        """
        FR : Constructeur de la classe IRacing\n
        EN : Constructor of the IRacing class
        """
        self.__ir = irsdk.IRSDK()

    def __idx_of_behind_player(self) -> int:
        """
        FR : Méthode privée permettant de récupérer l'index de la voiture derrière l'utilisateur\n
        EN : Private method to get the index of the car behind the user
        :return: (int)
            FR : Index de la voiture derrière l'utilisateur
            EN : Index of the car behind the user
        """
        return self.__ir['CarIdxPosition'].index(self.__ir['PlayerCarPosition'] + 1)

    def __idx_of_ahead_player(self) -> int:
        """
        FR : Méthode privée permettant de récupérer l'index de la voiture devant l'utilisateur\n
        EN : Private method to get the index of the car ahead of the user
        :return: (int)
            FR : Index de la voiture au classement devant l'utilisateur
            EN : Index of the car in the ranking ahead of the user
        """
        return self.__ir['CarIdxPosition'].index(self.__ir['PlayerCarPosition'] - 1)

    def __idx_of_ahead_car(self) -> int:
        """
        FR : Méthode privée permettant de récupérer l'index de la voiture devant l'utilisateur\n
        EN : Private method to get the index of the car ahead of the user
        :return:
            FR : Index de la voiture devant l'utilisateur
            EN : Index of the car ahead of the user
        """
        closest_car_idx = -1
        min_distance_diff = float('inf')
        for idx, distance in enumerate(self.__ir["CarIdxLapDistPct"]):
            if idx == -1 or distance == -1 or idx == self.__ir["PlayerCarIdx"]:
                continue
            if distance < self.__ir["CarIdxLapDistPct"][self.__ir["PlayerCarIdx"]]:
                continue
            distance_diff = abs(self.__ir["CarIdxLapDistPct"][self.__ir["PlayerCarIdx"]] - distance)
            if distance_diff > 0.5:
                continue
            if distance_diff < min_distance_diff:
                min_distance_diff = distance_diff
                closest_car_idx = idx
        return closest_car_idx

    def __idx_of_behind_car(self) -> int:
        """
        FR : Méthode privée permettant de récupérer l'index de la voiture derrière l'utilisateur\n
        EN : Private method to get the index of the car behind the user
        :return: (int)
            FR : Index de la voiture derrière l'utilisateur
            EN : Index of the car behind the user
        """
        closest_car_idx = -1
        min_distance_diff = float('inf')
        for idx, distance in enumerate(self.__ir["CarIdxLapDistPct"]):
            if idx == -1 or distance == -1 or idx == self.__ir["PlayerCarIdx"]:
                continue
            distance_diff = abs(self.__ir["CarIdxLapDistPct"][self.__ir["PlayerCarIdx"]] - distance)
            if distance_diff < 0.5 and distance > self.__ir["CarIdxLapDistPct"][self.__ir["PlayerCarIdx"]]:
                continue
            if distance_diff > 0.5:
                distance_diff = abs(1 - distance_diff)
            if distance_diff < min_distance_diff:
                min_distance_diff = distance_diff
                closest_car_idx = idx
        return closest_car_idx

    def __is_hotlap(self) -> bool:
        """
        FR : Méthode privée permettant de savoir si l'utilisateur est en hotlap ou non\n
        EN : Private method to know if the user is in a hotlap or not
        :return: (bool)
            FR : True si l'utilisateur est en hotlap, False sinon
            EN : True if the user is in a hotlap, False otherwise
        """
        return self.__ir['SessionTimeRemain'] == -1

    def __is_race_mesured_laps(self) -> bool:
        """
        FR : Méthode privée permettant de savoir si la course est mesurée en tours ou non\n
        EN : Private method to know if the race is measured in laps or not
        :return: (bool)
            FR : True si la course est mesurée en tours, False sinon
            EN : True if the race is measured in laps, False otherwise
        """
        return self.__ir['SessionTimeTotal'] == 86400.0

    def __is_race_mesured_time(self) -> bool:
        """
        FR : Méthode privée permettant de savoir si la course est mesurée en temps ou non\n
        EN : Private method to know if the race is measured in time or not
        :return: (bool)
            FR : True si la course est mesurée en temps, False sinon
            EN : True if lap is measured in time, False otherwise
        """
        return self.__ir['SessionLapsRemainEx'] == 32767

    def __is_race_over(self) -> bool:
        """
        FR : Méthode privée permettant de savoir si la course est terminée ou non\n
        EN : Private method to know if the race is ended or not
        :return: (bool)
            FR : True si la course est terminée, False sinon
            EN : True if the race is over, False otherwise
        """
        return (self.__ir['SessionTimeRemain'] == 0 and self.__is_race_mesured_time()) or (
                self.__ir['SessionLapsRemainEx'] == 0 and self.__is_race_mesured_laps())

    def __best_session_lap_time(self) -> float:
        """
        FR : Méthode privée permettant de récupérer le meilleur tour de la session\n
        EN : Private method to get the best lap time of the session
        :return: (float)
            FR : Meilleur tour de la session
            EN : Best lap time of the session
        """
        min_lap_time = float('inf')
        for lap_time in self.__ir["CarIdxBestLapTime"]:
            if lap_time < min_lap_time and lap_time != -1:
                min_lap_time = lap_time
        return min_lap_time

    def connect(self):
        """
        FR : Méthode permettant de se connecter à IRacing\n
        EN : Method to connect to IRacing
        """
        self.__ir.startup()
        if not self.__ir.is_initialized:
            raise IRacingError("IRacing not initialized")

    def thread_fuel_consumption(self) -> None:
        """
        FR : Thread permettant de récupérer la moyenne de carburant consommé tant que la session est en cours\n
        EN : Thread to get the average fuel consumption as long as the session is in progress
        """
        global repetition, fuel_consumption_by_hour, average_fuel_consumption_by_second
        repetition = 0
        fuel_consumption_by_hour = 0

        while not self.__is_race_over():
            fuel_consumption_by_hour += self.__ir['FuelUsePerHour']
            repetition += 1
            average_fuel_consumption_by_second = fuel_consumption_by_hour / repetition / 3600
            sleep(0.1)
        print("Fin de la course")

    def my_position(self) -> str:
        """
        FR : Méthode permettant de récupérer la position de l'utilisateur\n
        EN : Method to get the user's position
        :return: (str)
            FR : Position de l'utilisateur
            EN : User's position
        """
        return str(self.__ir['PlayerCarPosition'])

    def count_total_laps(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de tours total de la course\n
        EN : Method to get the total number of laps of the race
        :return: (str)
            FR : Nombre de tours total de la course
            EN : Total number of laps of the race
        """
        if self.__is_race_mesured_laps():
            return DataConverter.int_to_laps_number(self.__ir['SessionLapsTotal'])
        else:
            return self.duration_race()

    def count_remaining_laps(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de tours restants de la course\n
        EN : Method to get the remaining
        :return: (str)
            FR : Nombre de tours restants de la course
            EN : Number of remaining laps of the race
        """
        if self.__is_race_mesured_laps():
            return DataConverter.int_to_laps_number(self.__ir['SessionLapsRemainEx'])
        else:
            return self.duration_remaining()

    def duration_race(self) -> str:
        """
        FR : Méthode permettant de récupérer la durée totale de la course\n
        EN : Method to get the total duration of the race
        :return: (str)
            FR : Durée totale formatée de la course
            EN : Formatted total duration of the race
        """
        if self.__is_race_mesured_time():
            return DataConverter.format_lap_time(self.__ir['SessionTimeTotal'])
        else:
            return self.count_total_laps()

    def duration_remaining(self) -> str:
        """
        FR : Méthode permettant de récupérer la durée restante de la course\n
        EN : Method to get the remaining duration
        :return: (str)
            FR : Durée restante formatée de la course
            EN : Formatted remaining duration
        """
        if self.__is_race_mesured_time():
            return DataConverter.format_lap_time(self.__ir['SessionTimeRemain'])
        else:
            return self.count_remaining_laps()

    def my_best_lap_time(self) -> str:
        """
        FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur\n
        EN : Method to get the best lap time of the user
        :return: (str)
            FR : Temps formaté du meilleur tour de l'utilisateur
            EN : Formatted time of the best lap of the user
        """
        best_lap_time = self.__ir['LapBestLapTime']
        return DataConverter.format_lap_time(best_lap_time)

    def my_last_lap_time(self) -> str:
        """
        FR : Méthode permettant de récupérer le dernier tour de l'utilisateur\n
        EN : Method to get the last lap time of the user
        :return: (str)
            FR : Temps formaté du dernier tour de l'utilisateur
            EN : Formatted time of the last lap of the user
        """
        last_lap_time = self.__ir['LapLastLapTime']
        return DataConverter.format_lap_time(last_lap_time)

    def incident_count(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre d'incidents de l'utilisateur\n
        EN : Method to get the number of incidents of the user
        :return: (int)
            FR : Nombre d'incidents de l'utilisateur
            EN : Number of incidents of the user
        """
        return str(self.__ir['PlayerCarMyIncidentCount'])

    def best_session_lap_time(self) -> str:
        """
        FR : Méthode permettant de récupérer le meilleur tour de la session\n
        EN : Method to get the best lap time of the session
        :return: (str)
            FR : Temps formaté du meilleur tour de la session
            EN : Formatted time of the best lap of the session
        """
        return DataConverter.format_lap_time(self.__best_session_lap_time())

    def best_lap_time_ahead_car(self) -> str:
        """
        FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur devant\n
        EN : Method to get the best lap time of the user ahead
        :return: (str)
            FR : Temps formaté du meilleur tour de l'utilisateur devant
            EN : Formatted time of the best lap of the user ahead
        """
        best_lap_time = self.__ir['CarIdxBestLapTime'][self.__idx_of_ahead_player()]
        return DataConverter.format_lap_time(best_lap_time)

    def last_lap_time_ahead_car(self) -> str:
        """
        FR : Méthode permettant de récupérer le dernier tour de l'utilisateur devant
        EN : Method to get the last lap time of the user ahead
        :return: (str)
            FR : Temps formaté du dernier tour de l'utilisateur devant
            EN : Formatted time of the last lap of the user ahead
        """
        last_lap_time = self.__ir['CarIdxLastLapTime'][self.__idx_of_ahead_player()]
        return DataConverter.format_lap_time(last_lap_time)

    def best_lap_time_behind_car(self) -> str:
        """
        FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur derrière\n
        EN : Method to get the best lap time of the user behind
        :return: (str)
            FR : Temps formaté du meilleur tour de l'utilisateur derrière
            EN : Formatted time of the best lap of the user behind
        """
        best_lap_time = self.__ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return DataConverter.format_lap_time(best_lap_time)

    def last_lap_time_behind_car(self) -> str:
        """
        FR : Méthode permettant de récupérer le dernier tour de l'utilisateur derrière\n
        EN : Method to get the last lap time of the user behind
        :return: (str)
            FR : Temps formaté du dernier tour de l'utilisateur derrière
            EN : Formatted time of the last lap of the user behind
        """
        last_lap_time = self.__ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return DataConverter.format_lap_time(last_lap_time)

    def declared_wet(self) -> str:
        """
        FR : Méthode permettant de savoir si les pneus pluie sont autorisés ou non\n
        EN : Method to know if wet tires are allowed or not
        :return: (bool)
            FR : True si les pneus pluie sont autorisés, False sinon
            EN : True if wet tires are allowed, False otherwise
        """
        return str(self.__ir['WeatherDeclaredWet'] == 1)

    def pourcentage_humidity(self) -> str:
        """
        FR : Méthode récupérant le pourcentage d'humidité\n
        EN : Method to get the humidity percentage
        :return: (str)
            FR : Pourcentage d'humidité
            EN : Humidity percentage
        """
        return DataConverter.int_to_pourcentage(self.__ir['RelativeHumidity'])

    def pourcentage_precipation(self) -> str:
        """
        FR : Méthode récupérant le pourcentage de précipitation\n
        EN : Method to get the precipitation percentage
        :return: (str)
            FR : Pourcentage de précipitation
            EN : Precipitation percentage
        """
        return DataConverter.int_to_pourcentage(self.__ir['Precipitation'])

    def remaining_litres_of_fuel(self) -> str:
        """
        FR : Méthode récupérant les litres restants de carburant\n
        EN : Method to get the remaining liters of fuel
        :return: (str)
            FR : Litres restants de carburant
            EN : Remaining liters of fuel
        """
        return DataConverter.int_to_liters(self.__ir['FuelLevel'])

    def remaining_pourcentage_of_fuel(self) -> str:
        """
        FR : Méthode récupérant le pourcentage restant de carburant\n
        EN : Method to get the remaining percentage of fuel
        :return: (str)
            FR : Pourcentage restant de carburant
            EN : Remaining percentage of fuel
        """
        return DataConverter.int_to_pourcentage(self.__ir['FuelLevelPct'])

    def get_fuel_necessary(self) -> str:
        """
        FR : Méthode afin de calculer les litres nécéssaires de carburant pour terminer la course\n
        EN :  Method to calculate the necessary liters of fuel to finish the race
        :return: (str)
            FR : Litres de carburant nécéssaires pour finir la course
            EN : Liters of fuel necessary to finish the race
        """
        if average_fuel_consumption_by_second:
            return "Le calculateur n'a pas été démarré"
        fuel_necessary = 0
        if self.__is_race_mesured_laps():
            fuel_necessary = self.count_remaining_laps() * self.__ir[
                'LapLastLapTime'] * average_fuel_consumption_by_second - self.__ir['FuelLevel']
        elif self.__is_race_mesured_time():
            fuel_necessary = self.__ir['SessionTimeRemain'] * average_fuel_consumption_by_second - self.__ir['FuelLevel']

        if fuel_necessary < 0:
            return "Vous avez assez de carburant"
        else:
            return f"Il manque {fuel_necessary}L de carburant pour finir la course."

    def gap_with_front_car(self) -> str:
        """
        FR : Méthode afin de calculer l'écart avec la voiture devant l'utilisateur\n
        EN : Method to calculate the gap with the car ahead of the user
        :return: (str)
            FR : Temps relatif formaté avec la voiture devant
            EN : Formatted relative time with the car ahead
        """
        player_est_time = self.__ir["CarIdxEstTime"][self.__ir["PlayerCarIdx"]]
        car_idx = self.__idx_of_ahead_car()
        if car_idx == -1:
            return "Aucune voiture devant vous"
        car_est_time = self.__ir["CarIdxEstTime"][car_idx]
        relative_time = car_est_time - player_est_time
        return DataConverter.format_lap_time(relative_time)

    def gap_with_behind_car(self) -> str:
        """
        FR : Méthode permettant de calculer l'écart avec la voiture derrière l'utilisateur\n
        EN : Method to calculate the gap with the car behind the user
        :return: (str)
            FR : Temps relatif formaté avec la voiture derrière
            EN : Formatted relative time with the car behind
        """
        player_est_time = self.__ir["CarIdxEstTime"][self.__ir["PlayerCarIdx"]]
        car_idx = self.__idx_of_behind_car()
        if car_idx == -1:
            return "Aucune voiture derrière vous"
        car_est_time = self.__ir["CarIdxEstTime"][car_idx]
        if car_est_time < player_est_time:
            relative_time = player_est_time - car_est_time
        else:
            relative_time = self.__best_session_lap_time() - car_est_time
        return DataConverter.format_lap_time(relative_time - 1.5)

    def get_wet_tires(self) -> None:
        """
        FR : Méthode permettant de mettre les pneus pluies à l'utilisateur\n
        EN : Method to put wet tires to the user
        """
        self.__ir.pit_command(irsdk.PitCommandMode.type_tires, 1)

    def get_dry_tires(self) -> None:
        """
        FR : Méthode permettant de mettre les pneus secs à l'utilisateur\n
        EN : Method to put dry tires to the user
        """
        self.__ir.pit_command(irsdk.PitCommandMode.type_tires, 0)

    def add_fuel(self, fuel_quantity: int) -> None:
        """
        FR : Méthode permettant d'ajouter les litres de carburant demandés\n
        EN : Method to add the requested liters of fuel
        :param fuel_quantity: (int)
            FR : Litres de carburant à ajouter
            EN : Liters of fuel to add
        """
        self.__ir.pit_command(irsdk.PitCommandMode.fuel, fuel_quantity)

    def change_front_left_tire(self) -> None:
        """
        FR : Méthode permettant de changer le pneu avant gauche\n
        EN : Method to change the front left tire
        """
        self.__ir.pit_command(irsdk.PitCommandMode.lf)

    def change_rear_left_tire(self) -> None:
        """
        FR : Méthode permettant de changer le pneu arrière gauche\n
        EN : Method to change the rear left tire
        """
        self.__ir.pit_command(irsdk.PitCommandMode.lr)

    def change_front_right_tire(self) -> None:
        """
        FR : Méthode permettant de changer le pneu avant droit\n
        EN : Method to change the front right tire
        """
        self.__ir.pit_command(irsdk.PitCommandMode.rf)

    def change_rear_right_tire(self) -> None:
        """
        FR : Méthode permettant de changer le pneu arrière droit\n
        EN : Method to change the rear right tire
        """
        self.__ir.pit_command(irsdk.PitCommandMode.rr)

    def count_sets_of_tires(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de sets de pneus disponibles\n
        EN : Method to get the number of tire sets available
        :return: (str)
            FR : Nombre de sets de pneus disponibles
            EN : Number of tire sets available
        """
        count = self.__ir['TireSetsAvailable']
        if count == 255 or count is None:
            return "Infini"
        return str(count)

    def count_sets_of_front_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de pneus avant droit disponibles\n
        EN : Method to get the number of front right tires available
        :return: (str)
            FR : Nombre de pneus avant droit disponibles
            EN : Number of front right tires available
        """
        count = self.__ir['RFTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return str(count)

    def temperature_of_front_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer la température du pneu avant droit\n
        EN : Method to get the temperature of the front right tire
        :return: (str)
            FR : Température moyenne du pneu avant droit en degrés Celsius à partir du flanc gauche, central et droit.
            EN : The average temperature of the front right tire in Celsius degrees from the left, middle, and right carcass.
        """
        return DataConverter.float_to_celsius_degrees(
            (self.__ir['RFtempCL'] + self.__ir['RFtempCM'] + self.__ir['RFtempCR']) / 3)

    def remaining_percentage_of_front_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le pourcentage restant du pneu avant droit\n
        EN : Method to get the remaining percentage of the front right tire
        :return: (str)
            FR : Pourcentage moyen du pneu avant droit à partir du flanc gauche, central et droit.
            EN : The average percentage of the front right tire from the left, middle, and right carcass.
        """
        return DataConverter.float_to_pourcentage((self.__ir['RFwearL'] + self.__ir['RFwearM'] + self.__ir['RFwearR']) / 3)

    def count_sets_of_rear_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de pneus arrière droit disponibles\n
        EN : Method to get the number of rear right tires available
        :return:
            FR : Nombre de pneus arrière droit disponibles
            EN : Number of rear right tires available
        """
        count = self.__ir['RRTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return str(count)

    def temperature_of_rear_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer la température du pneu arrière droit\n
        EN : Method to get the temperature of the rear right tire
        :return: (str)
            FR : Température moyenne du pneu arrière droit en degrés Celsius à partir du flanc gauche, central et droit.
            EN : The average temperature of the rear right tire in Celsius degrees from the left, middle, and right carcass.
        """
        return DataConverter.float_to_celsius_degrees(
            (self.__ir['RRtempCL'] + self.__ir['RRtempCM'] + self.__ir['RRtempCR']) / 3)

    def remaining_percentage_of_rear_right_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le pourcentage restant du pneu arrière droit\n
        EN : Method to get the remaining percentage of the rear right tire
        :return: (str)
            FR: Pourcentage moyen du pneu arrière droit à partir du flanc gauche, central et droit.
            EN: The average percentage of the rear right tire from the left, middle, and right carcass.
        """
        return DataConverter.float_to_pourcentage((self.__ir['RRwearL'] + self.__ir['RRwearM'] + self.__ir['RRwearR']) / 3)

    def count_sets_of_front_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de pneus avant gauche disponibles\n
        EN : Method to get the number of front left tires available
        :return: (str)
            FR : Nombre de pneus avant gauche disponibles
            EN : Number of front left tires available
        """
        count = self.__ir['LFTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return str(count)

    def temperature_of_front_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer la température du pneu avant gauche\n
        EN : Method to get the temperature of the front left tire
        :return: (str)
            FR : Température moyenne du pneu avant gauche en degrés Celsius à partir du flanc gauche, central et droit.
            EN : The average temperature of the front left tire in Celsius degrees from the left, middle, and right carcass.
        """
        return DataConverter.float_to_celsius_degrees(
            (self.__ir['LFtempCL'] + self.__ir['LFtempCM'] + self.__ir['LFtempCR']) / 3)

    def remaining_percentage_of_front_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le pourcentage restant du pneu avant gauche\n
        EN : Method to get the remaining percentage of the front left tire
        :return: (st)
            FR : Pourcentage moyen du pneu avant gauche à partir du flanc gauche, central et droit.
            EN : The average percentage of the front left tire from the left, middle, and right carcass.
        """
        return DataConverter.float_to_pourcentage((self.__ir['LFwearL'] + self.__ir['LFwearM'] + self.__ir['LFwearR']) / 3)

    def count_sets_of_rear_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le nombre de pneus arrière gauche disponibles\n
        EN : Method to get the number of rear left tires available
        :return: (str)
            FR : Nombre de pneus arrière gauche disponibles
            EN : Number of rear left tires available
        """
        count = self.__ir['LRTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return str(count)

    def temperature_of_rear_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer la température du pneu arrière gauche.\n
        EN : Method to get the temperature of the rear left tire
        :return: (str)
            FR : Température moyenne du pneu arrière gauche en degrés Celsius à partir du flanc gauche, central et droit.
            EN : The average temperature of the rear left tire in Celsius degrees from the left, middle, and right carcass.
        """
        return DataConverter.float_to_celsius_degrees(
            (self.__ir['LRtempCL'] + self.__ir['LRtempCM'] + self.__ir['LRtempCR']) / 3)

    def remaining_percentage_of_rear_left_tire(self) -> str:
        """
        FR : Méthode permettant de récupérer le pourcentage restant du pneu arrière gauche\n
        EN : Method to get the remaining percentage of the rear left tire
        :return: (str)
            FR : Pourcentage moyen du pneu arrière gauche à partir du flanc gauche, central et droit.
            EN : The average percentage of the rear left tire from the left, middle, and right cOarcass.
        """
        return DataConverter.float_to_pourcentage((self.__ir['LRwearL'] + self.__ir['LRwearM'] + self.__ir['LRwearR']) / 3)
