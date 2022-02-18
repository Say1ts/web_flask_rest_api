import pandas as pd
import re
import random as rd


def load_data():
    """Return pandas dataframe with geographic information. Assign names to columns."""
    df = pd.read_csv('RU.txt',
                     header=None,
                     sep='\t',
                     low_memory=False,
                     names=['geonameid', 'name', 'asciiname',
                            'alternatenames', 'latitude', 'longitude',
                            'feature class', 'feature code', 'country code', 'cc2',
                            'admin1 code', 'admin2 code', 'admin3 code',
                            'admin4 code', 'population', 'elevation',
                            'dem', 'timezone', 'modification date']
                     )
    df.drop(columns=['cc2'], axis=1, inplace=True)
    return df


def load_timezones():
    """Return pandas dataframe with time zones for calculate time differences."""
    df_timezones = pd.read_csv('timeZones.txt',
                               sep='\t',
                               low_memory=False
                               )
    df_timezones.drop(columns=['CountryCode', 'DST offset 1. Jul 2022',
                               'rawOffset (independant of DST)'], axis=1, inplace=True)
    return df_timezones


def show_info_by_geonameid(geonameid, df):
    """Return dictionary with information about city."""
    info = df[df.geonameid == geonameid] \
        .to_dict(orient="records")
    status = 404 if info == [] else 200
    description = 'City is not found' if info == [] else 'OK'
    res = dict(status=status,
               description=description,
               info=info)
    return res


def show_info_page(page, number, df):
    """Return dictionary with information about cities by
    received page and count of cities on page.
    """
    start = number * page
    stop = number + number * page
    sample = df.iloc[start:stop].to_dict(orient="records")

    status = 404 if sample == [] else 200
    description= 'Out of range' if sample == [] else 'OK'
    res = dict(
        status=status,
        description=description,
        pages=sample)

    return res


def find_town_by_name(name, df):
    mask = df["alternatenames"].str.contains(f"{name}", na=False)
    res = df.loc[mask].sort_values(by=['population'], ascending=False)
    return res


def find_delta_time(timezone1, timezone2, df_timezones):
    a = df_timezones[df_timezones.TimeZoneId == f'{timezone1}'].iloc[0, 1]
    b = df_timezones[df_timezones.TimeZoneId == f'{timezone2}'].iloc[0, 1]
    return abs(a - b)


def find_north_ans(first_town, second_town, name_1, name_2):
    if first_town.iloc[4] > second_town.iloc[4]:
        text = f'Город {name_1} находится севернее, чем город {name_2}. <br>'
        north = name_1
    else:
        text = f'Город {name_2} находится севернее, чем город {name_1}. <br>'
        north = name_2
    return text, north


def find_delta_time_text(first_town, second_town):
    timezone1 = first_town.iloc[16]
    timezone2 = second_town.iloc[16]
    delta = find_delta_time(timezone1, timezone2, load_timezones())
    if timezone1 == timezone2:
        text = f'Города находится в одном часовом поясе.'
    else:
        text = f'Разница в часовых поясах городов составляет {int(delta)} ч.'
    return text


def try_to_find_town_by_name(name, df):
    try:
        city = find_town_by_name(name, df).iloc[0]
    except Exception:
        status = 404
        city = []
        description = f'{name} is not found'
        return status, city, description
    else:
        status = 200
        description = 'Ok'
        return status, city, description


def return_result_according_status(status_1, city_1, description_1,
                                   status_2, city_2, description_2, name_1, name_2):
    if status_1 == status_2 == 200:
        info_united = city_1.to_frame() \
            .join(city_2).T \
            .to_dict(orient="records")

        text_description_north, north = find_north_ans(city_1, city_2, name_1, name_2)
        res = dict(
            status=200,
            description='OK',
            north=north,
            text_description_north=text_description_north,
            delta_time=find_delta_time_text(city_1, city_2),
            info_about_cities=info_united
        )
    elif status_1 == 404:
        res = dict(status=status_1,
                   description=description_1)
    else:
        res = dict(status=status_2,
                   description=description_2)
    return res


def show_info_for_two_towns(name_1, name_2, df):
    """Return dictionary with information about 2 cities
    and show which north, how much time difference.
    """
    status_1, city_1, description_1 = try_to_find_town_by_name(name_1, df)
    status_2, city_2, description_2 = try_to_find_town_by_name(name_2, df)
    return return_result_according_status(
        status_1, city_1, description_1,
        status_2, city_2, description_2, name_1, name_2)


def show_guessed_town_name(name, df):
    """Return dictionary with list of guessed names by received part"""
    match_names_df = find_town_by_name(name, df)[0:10]
    match_names_df = match_names_df['alternatenames'].str.split(pat=" |,|\n")
    correct_list_of_names = []
    for series_with_names in match_names_df:
        for current_name in series_with_names:
            if re.search(f'{name}', current_name):
                correct_list_of_names.append(current_name)
    status = 404 if correct_list_of_names == [] else 200
    return dict(status=status, guessed_names=correct_list_of_names)


def show_not_found():
    """Return dictionary with status 404 if there are no such page"""
    return dict(status=404,
                description='The page is not found')


def test_with_random_results():
    """Function for testing program with some cases."""
    x = load_data()
    number = rd.randint(0, 363823)

    count_on_page = rd.randint(1, 100)

    page = int(count_on_page / 363823)
    wrong_page = 100000000000

    geonameid = x.iloc[number][0]
    wrong_geonameid = 0

    print(number)
    print('Проверка первого метода:',
          'ОК', show_info_by_geonameid(geonameid, x), '\n',
          'Несуществующий geonameid', show_info_by_geonameid(wrong_geonameid, x), '\n\n')
    print('Проверка второго метода:',
          'ОК', show_info_page(page, count_on_page, x), '\n',
          'Номер страницы задан больше существующей', show_info_page(wrong_page, count_on_page, x), '\n\n')
    print('Проверка третьего метода:',
          'ОК', show_info_for_two_towns('Томск', 'Москва', x), '\n',
          'Отсутствие города №1', show_info_for_two_towns('wrong_city1', 'Москва', x), '\n',
          'Отсутствие города №2', show_info_for_two_towns('Томск', 'wrong_city2', x), '\n\n')
    print('Проверка четвертого метода:',
          'ОК', show_guessed_town_name('Санкт', x), '\n',
          'Не найдено соответствие', show_guessed_town_name('wrong_city', x), '\n')


if __name__ == '__main__':
    test_with_random_results()
