from asyncio import sleep

import irsdk


class IRacing:
    def __init__(self):
        self.ir = irsdk.IRSDK()
        self.ir.startup()

    def __format_lap_time(self, lap_time: float) -> str:
        return f"{int(lap_time / 60)}:{lap_time % 60:.3f}"

    def __int_to_pourcentage(self, i: int) -> str:
        return f"{i}%"

    def __int_to_liters(self, i: int) -> str:
        return f"{i}L"

    def __idx_of_behind_player(self) -> int:
        return self.ir['CarIdxPosition'].index(self.my_position() + 1)

    def __idx_of_ahead_player(self) -> int:
        return self.ir['CarIdxPosition'].index(self.my_position() - 1)

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

    def __is_hotlap(self) -> bool:
        return self.ir['SessionTimeRemain'] == -1

    def __is_race_mesured_laps(self) -> bool:
        return self.ir['SessionTimeTotal'] == 86400.0

    def __is_race_mesured_time(self) -> bool:
        return self.ir['SessionLapsRemainEx'] == 32767

    def __is_race_over(self) -> bool:
        return (self.ir['SessionTimeRemain'] == 0 and self.__is_race_mesured_time()) or (
                self.ir['SessionLapsRemainEx'] == 0 and self.__is_race_mesured_laps())

    def __best_session_lap_time(self):
        min_lap_time = float('inf')
        for lap_time in self.ir["CarIdxBestLapTime"]:
            if lap_time < min_lap_time and lap_time != -1:
                min_lap_time = lap_time
        return min_lap_time

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

    # Ma Position
    def my_position(self) -> int:
        return self.ir['PlayerCarPosition']

    # Nombre de tours total dans la course
    def count_total_laps(self) -> str:
        if self.__is_race_mesured_laps():
            return self.ir['SessionLapsTotal']
        else:
            return self.duration_race()

    # Nombre de tours restants dans la course
    def count_remaining_laps(self) -> str:
        if self.__is_race_mesured_laps():
            return self.ir['SessionLapsRemainEx']
        else:
            return self.duration_remaining()

    # Durée totale de la course
    def duration_race(self) -> str:
        if self.__is_race_mesured_time():
            return self.__format_lap_time(self.ir['SessionTimeTotal'])
        else:
            return self.count_total_laps()

    # Durée restante de la course
    def duration_remaining(self) -> str:
        if self.__is_race_mesured_time():
            return self.__format_lap_time(self.ir['SessionTimeRemain'])
        else:
            return self.count_remaining_laps()

    # Mon meilleur temps au tour
    def my_best_lap_time(self) -> str:
        best_lap_time = self.ir['LapBestLapTime']
        return self.__format_lap_time(best_lap_time)

    # Mon dernier temps au tour
    def my_last_lap_time(self) -> str:
        last_lap_time = self.ir['LapLastLapTime']
        return self.__format_lap_time(last_lap_time)

    # Mon nombre d'incidents
    def incident_count(self) -> int:
        return self.ir['PlayerCarMyIncidentCount']

    # Meilleur tour de la session
    def best_session_lap_time(self) -> str:
        return self.__format_lap_time(self.__best_session_lap_time())

    # Meilleur temps au tour de la voiture devant
    def best_lap_time_ahead_car(self) -> str:
        best_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_ahead_player()]
        return self.__format_lap_time(best_lap_time)

    # Dernier temps au tour de la voiture devant
    def last_lap_time_ahead_car(self) -> str:
        last_lap_time = self.ir['CarIdxLastLapTime'][self.__idx_of_ahead_player()]
        return self.__format_lap_time(last_lap_time)

    # Meilleur temps au tour de la voiture derrière
    def best_lap_time_behind_car(self) -> str:
        best_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return self.__format_lap_time(best_lap_time)

    # Dernier temps au tour de la voiture derrière
    def last_lap_time_behind_car(self) -> str:
        last_lap_time = self.ir['CarIdxBestLapTime'][self.__idx_of_behind_player()]
        return self.__format_lap_time(last_lap_time)

    # Autorisation des pneus pluie
    def declared_wet(self) -> bool:
        return self.ir['WeatherDeclaredWet'] == 1

    # Pourcentage de l'humidité
    def pourcentage_humidity(self) -> str:
        return self.__int_to_pourcentage(self.ir['RelativeHumidity'])

    # Pourcentage de précipitation
    def pourcentage_precipation(self) -> str:
        return self.__int_to_pourcentage(self.ir['Precipitation'])

    # Litres de carburant restant
    def remaining_litres_of_fuel(self) -> str:
        return self.__int_to_liters(self.ir['FuelLevel'])

    # Pourcentage de carburant restant
    def remaining_pourcentage_of_fuel(self) -> str:
        return self.__int_to_pourcentage(self.ir['FuelLevelPct'])

    # Carburant manquant pour finir la course
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

    # Ecart avec la voiture devant
    def gap_with_front_car(self):
        player_est_time = self.ir["CarIdxEstTime"][self.ir["PlayerCarIdx"]]
        car_idx = self.__idx_of_ahead_car()
        if car_idx == -1:
            return "Aucune voiture devant vous"
        car_est_time = self.ir["CarIdxEstTime"][car_idx]

        relative_time = car_est_time - player_est_time
        return self.__format_lap_time(relative_time)

    # Ecart avec la voiture derriere
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

        return self.__format_lap_time(relative_time - 1.5)

    def get_wet_tires(self):
        return self.ir.pit_command(irsdk.PitCommandMode.type_tires, 1)

    def get_dry_tires(self):
        return self.ir.pit_command(irsdk.PitCommandMode.type_tires, 0)

    def add_fuel(self, fuel_quantity: int):
        return self.ir.pit_command(irsdk.PitCommandMode.fuel, fuel_quantity)

    def change_tire_left_front(self):
        return self.ir.pit_command(irsdk.PitCommandMode.lf)

    def change_tire_left_rear(self):
        return self.ir.pit_command(irsdk.PitCommandMode.lr)

    def change_tire_right_front(self):
        return self.ir.pit_command(irsdk.PitCommandMode.rf)

    def change_tire_right_rear(self):
        return self.ir.pit_command(irsdk.PitCommandMode.rr)

    # TODO : PNEUS

    def get_count_set_tires_available(self):
        count = self.ir['TireSetsAvailable']
        if count == 255 or None:
            return "Infini"
        return count

    def get_set_right_front_tire_available(self):
        count = self.ir['RFTiresAvailable']
        if count == 255 or None:
            return "Infini"
        return count

    def get_temp_right_front_tire(self):
        return (self.ir['RFtempCL'] + self.ir['RFtempCM'] + self.ir['RFtempCR']) / 3

    def get_remaining_right_front_tire(self):
        return (self.ir['RFwearL'] + self.ir['RFwearM'] + self.ir['RFwearR']) / 3
