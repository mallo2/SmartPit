from asyncio import sleep
import irsdk

# FR : Méthode convertisseur d'un chrono de float à string
# EN :
def format_lap_time(lap_time: float) -> str:
    return f"{int(lap_time / 60)}:{lap_time % 60:.3f}"

# FR : Méthode convertisseur d'un chrono d'entier à un pourcentage
# EN :
def int_to_pourcentage(i: int) -> str:
    return f"{i}%"

# FR : Méthode convertisseur d'un chrono de float à un volume
# EN :
def int_to_liters(i: int) -> str:
    return f"{i}L"


class IRacing:
    def __init__(self):
        self.ir = irsdk.IRSDK()
        self.ir.startup()

    # FR : Méthode privée afin de récupérer l'index du joueur derrière l'utilisateur
    # EN :
    def __idx_of_behind_player(self) -> int:
        return self.ir['CarIdxPosition'].index(self.my_position() + 1)

    # FR : Méthode privée afin de récupérer l'index du joueur devant l'utilisateur
    # EN :
    def __idx_of_ahead_player(self) -> int:
        return self.ir['CarIdxPosition'].index(self.my_position() - 1)

    # FR : Méthode privée afin de récupérer l'index de la voiture devant l'utilisateur
    # EN :
    def __idx_of_ahead_car(self):
        closest_car_idx = -1
        min_distance_diff = float('inf')
        for idx, distance in enumerate(self.ir["CarIdxLapDistPct"]):
            if idx == -1 or distance == -1 or idx == self.ir["PlayerCarIdx"]:
                continue
            if distance < self.ir["CarIdxLapDistPct"][self.ir["PlayerCarIdx"]]:
                continue

            distance_diff = abs(self.ir["CarIdxLapDistPct"][self.ir["PlayerCarIdx"]] - distance)

            if distance_diff > 0.5:
                continue

            if distance_diff < min_distance_diff:
                min_distance_diff = distance_diff
                closest_car_idx = idx

        return closest_car_idx

    # FR : Méthode privée afin de récupérer l'index de la voiture derrière l'utilisateur
    # EN :
    def __idx_of_behind_car(self):
        closest_car_idx = -1
        min_distance_diff = float('inf')
        for idx, distance in enumerate(self.ir["CarIdxLapDistPct"]):
            if idx == -1 or distance == -1 or idx == self.ir["PlayerCarIdx"]:
                continue

            distance_diff = abs(self.ir["CarIdxLapDistPct"][self.ir["PlayerCarIdx"]] - distance)

            if distance_diff < 0.5 and distance > self.ir["CarIdxLapDistPct"][self.ir["PlayerCarIdx"]]:
                continue

            if distance_diff > 0.5:
                distance_diff = abs(1 - distance_diff)

            if distance_diff < min_distance_diff:
                min_distance_diff = distance_diff
                closest_car_idx = idx

        return closest_car_idx

    # FR : Méthode privée afin de savoir si l'utilisateur est dans un hotlap ou non
    # EN :
    def __is_hotlap(self) -> bool:
        return self.ir['SessionTimeRemain'] == -1

    # FR : Méthode privée afin de savoir si la session a un compteur de tour ou non
    # EN :
    def __is_race_mesured_laps(self) -> bool:
        return self.ir['SessionTimeTotal'] == 86400.0

    # FR : Méthode privée afin de savoir si la session a un compteur de temps ou non
    # EN :
    def __is_race_mesured_time(self) -> bool:
        return self.ir['SessionLapsRemainEx'] == 32767

    # FR : Méthode privée afin de savoir si la session est terminée ou non
    # EN :
    def __is_race_over(self) -> bool:
        return (self.ir['SessionTimeRemain'] == 0 and self.__is_race_mesured_time()) or (
                self.ir['SessionLapsRemainEx'] == 0 and self.__is_race_mesured_laps())

    # FR : Méthode privée afin de récupérer le meilleur tour de la session
    # EN :
    def __best_session_lap_time(self):
        min_lap_time = float('inf')
        for lap_time in self.ir["CarIdxBestLapTime"]:
            if lap_time < min_lap_time and lap_time != -1:
                min_lap_time = lap_time
        return min_lap_time

    # FR : Thread permettant de récuperer la moyenne de carburant consommé tant que la session est en cours
    # EN :
    def thread_fuel_consumption(self):
        global repetition, fuel_consumption_by_hour, average_fuel_consumption_by_second
        repetition = 0
        fuel_consumption_by_hour = 0

        while not self.__is_race_over():
            fuel_consumption_by_hour += self.ir['FuelUsePerHour']
            repetition += 1
            average_fuel_consumption_by_second = fuel_consumption_by_hour / repetition / 3600
            sleep(0.1)
        print("Fin de la course")

    # FR : Méthode pour récupérer la position de l'utilisateur
    # EN :
    def my_position(self) -> int:
        return self.ir['PlayerCarPosition']

    # FR : Méthode permettant de récupérer le nombre de tours total de la course
    # EN :
    def count_total_laps(self) -> str:
        if self.__is_race_mesured_laps():
            return self.ir['SessionLapsTotal']
        else:
            return self.duration_race()

    # FR : Méthode permettant de récupérer le nombre de tours restants de la course
    # EN :
    def count_remaining_laps(self) -> str:
        if self.__is_race_mesured_laps():
            return self.ir['SessionLapsRemainEx']
        else:
            return self.duration_remaining()

    # FR : Méthode permettant de récupérer la durée totale de la course
    # EN :
    def duration_race(self) -> str:
        if self.__is_race_mesured_time():
            return format_lap_time(self.ir['SessionTimeTotal'])
        else:
            return self.count_total_laps()

    # FR : Méthode permettant de récupérer la durée restante de la course
    # EN :
    def duration_remaining(self) -> str:
        if self.__is_race_mesured_time():
            return format_lap_time(self.ir['SessionTimeRemain'])
        else:
            return self.count_remaining_laps()

    # FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur
    # EN :
    def my_best_lap_time(self) -> str:
        best_lap_time = self.ir['LapBestLapTime']
        return format_lap_time(best_lap_time)

    # FR : Méthode permettant de récupérer le dernier tour de l'utilisateur
    # EN :
    def my_last_lap_time(self) -> str:
        last_lap_time = self.ir['LapLastLapTime']
        return format_lap_time(last_lap_time)

    # FR : Méthode permettant de récupérer le nombre d'incidents de l'utilisateur
    # EN :
    def incident_count(self) -> int:
        return self.ir['PlayerCarMyIncidentCount']

    # FR : Méthode permettant de récupérer le meilleur tour de la session
    # EN :
    def best_session_lap_time(self) -> str:
        return format_lap_time(self.__best_session_lap_time())

    # FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur devant
    # EN :
    def best_lap_time_ahead_car(self) -> str:
        best_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_ahead_player()]
        return format_lap_time(best_lap_time)

    # FR : Méthode permettant de récupérer le dernier tour de l'utilisateur devant
    # EN :
    def last_lap_time_ahead_car(self) -> str:
        last_lap_time = self.ir['CarIdxLastLapTime'][self.__idx_of_ahead_player()]
        return format_lap_time(last_lap_time)

    # FR : Méthode permettant de récupérer le meilleur tour de l'utilisateur derrière
    # EN :
    def best_lap_time_behind_car(self) -> str:
        best_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return format_lap_time(best_lap_time)

    # FR : Méthode permettant de récupérer le dernier tour de l'utilisateur derrière
    # EN :
    def last_lap_time_behind_car(self) -> str:
        last_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return format_lap_time(last_lap_time)

    # FR : Méthode permettant de savoir si les pneus pluie sont autorisés ou non
    # EN :
    def declared_wet(self) -> bool:
        return self.ir['WeatherDeclaredWet'] == 1

    # FR : Méthode récupérant le pourcentage d'humidité
    # EN :
    def pourcentage_humidity(self) -> str:
        return int_to_pourcentage(self.ir['RelativeHumidity'])

    # FR : Méthode récupérant le pourcentage de précipitation
    # EN :
    def pourcentage_precipation(self) -> str:
        return int_to_pourcentage(self.ir['Precipitation'])

    # FR : Méthode récupérant les litres restants de carburant
    # EN :
    def remaining_litres_of_fuel(self) -> str:
        return int_to_liters(self.ir['FuelLevel'])

    # FR : Méthode récupérant le pourcentage restant de carburant
    # EN :
    def remaining_pourcentage_of_fuel(self) -> str:
        return int_to_pourcentage(self.ir['FuelLevelPct'])

    # FR : Méthode afin de calculer les litres nécéssaires de carburant pour terminer la course
    # EN :
    def get_fuel_necessary(self) -> str:
        if average_fuel_consumption_by_second:
            return "Le calculateur n'a pas été démarré"
        fuel_necessary = 0
        if self.__is_race_mesured_laps():
            fuel_necessary = self.count_remaining_laps() * self.ir[
                'LapLastLapTime'] * average_fuel_consumption_by_second - self.ir['FuelLevel']
        elif self.__is_race_mesured_time():
            fuel_necessary = self.ir['SessionTimeRemain'] * average_fuel_consumption_by_second - self.ir['FuelLevel']

        if fuel_necessary < 0:
            return "Vous avez assez de carburant"
        else:
            return f"Il manque {fuel_necessary}L de carburant pour finir la course."

    # FR : Méthode afin de calculer l'écart avec la voiture devant l'utilisateur
    # EN :
    def gap_with_front_car(self):
        player_est_time = self.ir["CarIdxEstTime"][self.ir["PlayerCarIdx"]]
        car_idx = self.__idx_of_ahead_car()
        if car_idx == -1:
            return "Aucune voiture devant vous"
        car_est_time = self.ir["CarIdxEstTime"][car_idx]

        relative_time = car_est_time - player_est_time
        return format_lap_time(relative_time)

    # FR : Méthode afin de calculer l'écart avec la voiture derrière l'utilisateur
    # EN :
    def gap_with_behind_car(self):
        player_est_time = self.ir["CarIdxEstTime"][self.ir["PlayerCarIdx"]]
        car_idx = self.__idx_of_behind_car()
        if car_idx == -1:
            return "Aucune voiture derrière vous"
        car_est_time = self.ir["CarIdxEstTime"][car_idx]
        if car_est_time < player_est_time:
            relative_time = player_est_time - car_est_time
        else:
            relative_time = self.__best_session_lap_time() - car_est_time

        return format_lap_time(relative_time - 1.5)

    # FR : Méthode permettant de mettre les pneus pluies à l'utilisateur
    # EN :
    def get_wet_tires(self):
        return self.ir.pit_command(irsdk.PitCommandMode.type_tires, 1)

    # FR : Méthode permettant de mettre les pneus secs à l'utilisateur
    # EN :
    def get_dry_tires(self):
        return self.ir.pit_command(irsdk.PitCommandMode.type_tires, 0)

    # FR : Méthode permettant d'ajouter les litres de carburant demandés
    # EN :
    def add_fuel(self, fuel_quantity: int):
        return self.ir.pit_command(irsdk.PitCommandMode.fuel, fuel_quantity)

    # FR : Méthode permettant de changer le pneu avant gauche
    # EN :
    def change_front_left_tire(self):
        return self.ir.pit_command(irsdk.PitCommandMode.lf)

    # FR : Méthode permettant de changer le pneu arrière gauche
    # EN :
    def change_rear_left_tire(self):
        return self.ir.pit_command(irsdk.PitCommandMode.lr)

    # FR : Méthode permettant de changer le pneu avant droit
    # EN :
    def change_front_right_tire(self):
        return self.ir.pit_command(irsdk.PitCommandMode.rf)

    # FR : Méthode permettant de changer le pneu arrière gauche
    # EN :
    def change_rear_right_tire(self):
        return self.ir.pit_command(irsdk.PitCommandMode.rr)

    # FR : Méthode permettant de récuperer le nombre de sets de pneus disponibles
    # EN :
    def count_sets_of_tires(self):
        count = self.ir['TireSetsAvailable']
        if count == 255 or count is None:
            return "Infini"
        return count

    # FR : Méthode permettant de récuperer le nombre de pneus avant droit disponibles
    # EN :
    def count_sets_of_front_right_tire(self):
        count = self.ir['RFTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return count

    # FR : Méthode permettant de récuperer la température du pneu avant droit
    # EN :
    def temperature_of_front_right_tire(self):
        return (self.ir['RFtempCL'] + self.ir['RFtempCM'] + self.ir['RFtempCR']) / 3

    # FR : Méthode permettant de récuperer le pourcentage restant du pneu avant droit
    # EN :
    def remaining_percentage_of_front_right_tire(self):
        return (self.ir['RFwearL'] + self.ir['RFwearM'] + self.ir['RFwearR']) / 3

    # FR : Méthode permettant de récuperer le nombre de pneus arrière droit disponibles
    # EN :
    def count_sets_of_rear_right_tire(self):
        count = self.ir['RRTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return count

    # FR : Méthode permettant de récuperer la température du pneu arrière droit
    # EN :
    def temperature_of_rear_right_tire(self):
        return (self.ir['RRtempCL'] + self.ir['RRtempCM'] + self.ir['RRtempCR']) / 3

    # FR : Méthode permettant de récuperer le pourcentage restant du pneu arrière droit
    # EN :
    def remaining_percentage_of_rear_right_tire(self):
        return (self.ir['RRwearL'] + self.ir['RRwearM'] + self.ir['RRwearR']) / 3

    # FR : Méthode permettant de récuperer le nombre de pneus avant gauche disponibles
    # EN :
    def count_sets_of_front_left_tire(self):
        count = self.ir['LFTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return count

    # FR : Méthode permettant de récuperer la température du pneu avant gauche
    # EN :
    def temperature_of_front_left_tire(self):
        return (self.ir['LFtempCL'] + self.ir['LFtempCM'] + self.ir['LFtempCR']) / 3

    # FR : Méthode permettant de récuperer le pourcentage restant du pneu avant gauche
    # EN :
    def remaining_percentage_of_front_left_tire(self):
        return (self.ir['LFwearL'] + self.ir['LFwearM'] + self.ir['LFwearR']) / 3

    # FR : Méthode permettant de récuperer le nombre de pneus arrière gauche disponibles
    # EN :
    def count_sets_of_rear_left_tire(self):
        count = self.ir['LRTiresAvailable']
        if count == 255 or count is None:
            return "Infini"
        return count

    # FR : Méthode permettant de récuperer la température du pneu arrière gauche
    # EN :
    def temperature_of_rear_left_tire(self):
        return (self.ir['LRtempCL'] + self.ir['LRtempCM'] + self.ir['LRtempCR']) / 3

    # FR : Méthode permettant de récuperer le pourcentage restant du pneu arrière gauche
    # EN :
    def remaining_percentage_of_rear_left_tire(self):
        return (self.ir['LRwearL'] + self.ir['LRwearM'] + self.ir['LRwearR']) / 3
