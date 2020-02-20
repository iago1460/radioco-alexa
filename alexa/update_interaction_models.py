import json
import requests
from contextlib import suppress

# VARS
FILE_PATH_INPUT = 'interaction_models/template.json'
FILE_PATH_OUTPUT = 'interaction_models/radioco.json'
FILE_PATH_OUTPUT2 = 'interaction_models/cuacfm.json'

SHOWS_ENDPOINT = 'http://REPLACE_ME:8888/api/shows/'

# PHRASE SAMPLES
SYNONIM_OPEN = [
    'abre', 'ponme', 'pon', 'lanza', 'reproduce', 'dame',
    'ponga', 'abra', 'reproduzca', 'quiero'
]
SYNONIM_EPISODE = ['programa', 'capítulo', 'episodio', 'podcast']

PLAY_1 = '{SYNONIM_OPEN} el {{Episode_Ordinal}} {SYNONIM_EPISODE}'
PLAY_2 = '{SYNONIM_OPEN} el {SYNONIM_EPISODE} {{Episode_Number}}'

PLAY_ASK_1 = '{{Episode_Ordinal}} {SYNONIM_EPISODE}'
PLAY_ASK_2 = '{SYNONIM_EPISODE} {{Episode_Number}}'

PLAY_ASK_THE_1 = 'el {{Episode_Ordinal}} {SYNONIM_EPISODE}'
PLAY_ASK_THE_2 = 'el {SYNONIM_EPISODE} {{Episode_Number}}'

PLAY_SHORT_1 = '{SYNONIM_OPEN} {{Show}}'
PLAY_SHORT_2 = '{SYNONIM_OPEN} la {{Season_Ordinal}} temporada'

PLAY_SUFFIX_SEASSON_1 = ' de la {Season_Ordinal} temporada'
PLAY_SUFFIX_SEASSON_2 = ' de la temporada {Season_Number}'
PLAY_SUFFIX_SHOW = ' de {Show}'
PLAY_SUFFIX_STATION = ' en {Station}'


class Default(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def generate_samples():
    samples = set()
    for phrase in [PLAY_1, PLAY_2, PLAY_ASK_1, PLAY_ASK_2, PLAY_ASK_THE_1, PLAY_ASK_THE_2]:
        for value in SYNONIM_OPEN:
            tmp_1_phrase = str(phrase.format_map(Default(SYNONIM_OPEN=value)))
            for value in SYNONIM_EPISODE:
                tmp_phrase = str(tmp_1_phrase.format_map(Default(SYNONIM_EPISODE=value)))

                # mandatory prefix
                samples.add(tmp_phrase + PLAY_SUFFIX_SHOW)

                # optional season prefix
                samples.add(tmp_phrase + PLAY_SUFFIX_SEASSON_1 + PLAY_SUFFIX_SHOW)
                samples.add(tmp_phrase + PLAY_SUFFIX_SEASSON_2 + PLAY_SUFFIX_SHOW)

                # optional station
                samples.add(tmp_phrase + PLAY_SUFFIX_SEASSON_1 + PLAY_SUFFIX_SHOW + PLAY_SUFFIX_STATION)
                samples.add(tmp_phrase + PLAY_SUFFIX_SEASSON_2 + PLAY_SUFFIX_SHOW + PLAY_SUFFIX_STATION)

    for synonim in SYNONIM_OPEN:
        samples.add(PLAY_SHORT_1.format_map(Default(SYNONIM_OPEN=synonim)))
        samples.add(PLAY_SHORT_1.format_map(Default(SYNONIM_OPEN=synonim)) + PLAY_SUFFIX_STATION)

        samples.add(PLAY_SHORT_2.format_map(Default(SYNONIM_OPEN=synonim)) + PLAY_SUFFIX_SHOW)
        samples.add(PLAY_SHORT_2.format_map(Default(SYNONIM_OPEN=synonim)) + PLAY_SUFFIX_SHOW + PLAY_SUFFIX_STATION)

    return samples


def update_interaction():
    play_samples = sorted(generate_samples())
    INDEX_OF_PLAY = 4
    INDEX_OF_ORDINAL = 1
    INDEX_OF_SHOW = 0

    with open(FILE_PATH_INPUT, 'r') as file:
        interaction_model = json.load(file)

    # Play intent samples
    interaction_model['interactionModel']['languageModel']['intents'][INDEX_OF_PLAY]['samples'] = play_samples

    # Shows
    shows = requests.get(SHOWS_ENDPOINT).json()['results']

    shows_values = []
    for show in shows:
        show_data = {
            'id': show['id'],
            'name': {
                'value': show['title']
            }
        }
        if SHOW_SYNONYMS.get(show['title']):
            show_data['name']['synonyms'] = SHOW_SYNONYMS[show['title']]
        shows_values.append(show_data)
    interaction_model['interactionModel']['languageModel']['types'][INDEX_OF_SHOW]['values'] = shows_values

    # Ordinal
    ordinals = []
    for ordinal_name, ordinal_value in ORDINALS.items():
        ordinal = {
            'id': ordinal_value['id'],
            'name': {
                'value': ordinal_name,
            }
        }
        synonyms = ordinal_value['synonyms']
        with suppress(ValueError):
            synonyms.remove(ordinal_name)
        if synonyms:
            ordinal['name']['synonyms'] = synonyms
        ordinals.append(ordinal)
    interaction_model['interactionModel']['languageModel']['types'][INDEX_OF_ORDINAL]['values'] = ordinals

    with open(FILE_PATH_OUTPUT, 'w') as f:
        json.dump(interaction_model, f, sort_keys=True, indent=2)


    # CUAC
    with open(FILE_PATH_OUTPUT, 'r') as file:
        interaction_model = json.load(file)
    # 
    # shows = [item['name']['value'] for item in interaction_model['interactionModel']['languageModel']['types'][INDEX_OF_SHOW]['values']]
    # import pdb; pdb.set_trace()
    # return 1


    no_station_samples = sorted(set([
        sample for sample
        in interaction_model['interactionModel']['languageModel']['intents'][INDEX_OF_PLAY]['samples']
        if PLAY_SUFFIX_STATION not in sample
    ]))
    interaction_model['interactionModel']['languageModel']['intents'][INDEX_OF_PLAY]['samples'] = no_station_samples

    # TODO remove stations
    # apply name !

    with open(FILE_PATH_OUTPUT2, 'w') as f:
        json.dump(interaction_model, f, sort_keys=True, indent=2)


SHOW_SYNONYMS = {
    'A fume de carozo': [],
    'ACAMPA': [],
    'Alegria': [],
    'Algo pasa en Hollywood': [],
    'American Radio (Died Young)': [],
    'Ar de Coruña': [],
    'Azucar habanero': [],
    'Benditos Jueves': [],
    'CAMBIA si CAMBIO': [],
    'Café con gotas': [],
    'Circo Pirata': [],
    'Clima 69 | Roberto Doldán': [],
    'Cuac está a pasar': [],
    "Cuak'n'roll": [],
    'Cuidado corazón!': [],
    'Dale voz': [],
    'Debate das Eleccións á Reitoría da UDC 2015': [],
    'Dentro de un orden': [],
    'Día da Ciencia na Rúa': ['Ciencia en la calle'],
    'El Balcón': [],
    'El Desinformativo': [],
    'EnBoxes': ['En Boxes'],
    'EnWorking': [],
    'Especial CrossOver Revival': [],
    'Especial Festival Noroeste Estrella Galicia': [],
    'Falso Nueve': [],
    'Fantasma Accidental': [],
    'Folk in Trío': [],
    'Heima': [],
    'Internet de tu Color Favorito': [],
    'La Guardia de Walter': [],
    'La Juventud del Papa': [],
    'La Regadera': [],
    'La Tarde a Nuestra Manera': [],
    'La hora del Rock and Roll': [],
    'Loco Iván': [],
    'MARATON: CUAC RESISTE': ['maratón quack resiste'],
    'MARATON: CUAC VOLVE': ['maratón quack volvé', 'maratón quack vuelve'],
    'MalhumorHadas': [],
    'Manda carallo!': [],
    'Matinal Radio Vallekas: Especial Cuac FM #CuacResiste': [],
    'Mi rollo es el Rock': [],
    'Millennial': [],
    'Multiplex': [],
    'Novatos en emisión': [],
    'Nubes de Papel': [],
    'Ondas do Cárcere': [],
    'Orión 2.1': [],
    'PerforAcción': [],
    'Poca Broma!': [],
    'Que no es poco Especial Fin de Año': [],
    'R que R': [],
    'Radiantes FM': [],
    'Radio Barrio': [],
    'Radio Prometea': [],
    'RadioSénior': ['Radio Senior', 'Radio Sr.'],
    'Radioactiva': [],
    'Radiocassette': [],
    'Recendo': [],
    'Reportaxe polo Día da Muller': [],
    'Reversión': [],
    'Se va a liar... y lo sabes': [],
    'Simplemente Gente': [],
    'Sin Etiquetas': [],
    'Sopas con Onda': [],
    'Spoiler': [],
    'Tapas y raciones': [],
    'Trankimagazine': [],
    'Turbulencias': [],
    'Una noche en la ópera': [],
    'Xeración Bravú': [],
    'Y a ti qué te importa?': [],
    'Ábrete de orellas': []
}




ORDINALS = {
    'primer': {
        'id': 1,
        'synonyms': ['primero', 'primera']
    },
    'segundo': {
        'id': 2,
        'synonyms': ['segunda']}
    ,
    'tercer': {
        'id': 3,
        'synonyms': ['tercero', 'tercera']
    },
    'cuarto': {
        'id': 4,
        'synonyms': ['cuarta']
    },
    'quinto': {
        'id': 5,
        'synonyms': ['quinta']
    },
    'sexto': {
        'id': 6,
        'synonyms': ['sexta']
    },
    'séptimo': {
        'id': 7,
        'synonyms': ['séptima']
    },
    'octavo': {
        'id': 8,
        'synonyms': ['octava']
    },
    'noveno': {
        'id': 9,
        'synonyms': ['novena']
    },
    'décimo': {
        'id': 10,
        'synonyms': ['décima']
    },
    'undécimo': {
        'id': 11,
        'synonyms': ['decimoprimero', 'decimoprimer', 'décimo primero', 'décimo primer', 'undécima', 'decimoprimera', 'décima primera']
    },
    'duodécimo': {
        'id': 12,
        'synonyms': ['duodécimo', 'decimosegundo', 'décimo segundo', 'duodécima', 'decimosegunda', 'décima segunda']
    },
    'décimo tercero': {
        'id': 13,
        'synonyms': ['decimotercero', 'decimotercer', 'décimo tercero', 'décimo tercer', 'decimotercera', 'décima tercera']
    },
    'décimo cuarto': {
        'id': 14,
        'synonyms': ['decimocuarto', 'décimo cuarto', 'decimocuarta', 'décima cuarta']
    },
    'décimo quinto': {
        'id': 15,
        'synonyms': ['decimoquinto', 'décimo quinto', 'decimoquinta', 'décima quinta']
    },
    'décima sexto': {
        'id': 16,
        'synonyms': ['decimosexto', 'décimo sexto', 'decimosexta', 'décima sexta']
    },
    'décimo séptimo': {
        'id': 17,
        'synonyms': ['decimoséptimo', 'décimo séptimo', 'decimoséptima', 'décima séptima']
    },
    'décimo octavo': {
        'id': 18,
        'synonyms': ['decimoctavo', 'décimo octavo', 'decimoctava', 'décima octava']
    },
    'décimo noveno': {
        'id': 19,
        'synonyms': ['decimonoveno', 'décimo noveno', 'decimonovena', 'décima novena']
    },
    'vigésimo': {
        'id': 20,
        'synonyms': ['vigésima']
    },
    'vigésimo primero': {
        'id': 21,
        'synonyms': ['vigesimoprimero', 'vigésimo primero', 'vigesimoprimera', 'vigésima primera']
    },
    'vigésimo segundo': {
        'id': 22,
        'synonyms': ['vigesimosegundo', 'vigésimo segundo', 'vigesimosegunda', 'vigésima segunda']
    },
    'vigésimo tercero': {
        'id': 23,
        'synonyms': ['vigesimotercero', 'vigésimo tercero', 'vigesimotercera', 'vigésima tercera']
    },
    'vigésimo cuarto': {
        'id': 24,
        'synonyms': ['vigesimocuarto', 'vigésimo cuarto', 'vigesimocuarta', 'vigésima cuarta']
    },
    'vigésimo quinto': {
        'id': 25,
        'synonyms': ['vigesimoquinto', 'vigésimo quinto', 'vigesimoquinta', 'vigésima quinta']
    },
    'vigésimo sexto': {
        'id': 26,
        'synonyms': ['vigesimosexto', 'vigésimo sexto', 'vigesimosexta', 'vigésima sexta']
    },
    'vigésimo séptimo': {
        'id': 27,
        'synonyms': ['vigesimoséptimo', 'vigésimo séptimo', 'vigesimoséptima', 'vigésima séptima']
    },
    'vigésimo octavo': {
        'id': 28,
        'synonyms': ['vigesimoctavo', 'vigésimo octavo', 'vigesimoctava', 'vigésima octava']
    },
    'vigésimo noveno': {
        'id': 29,
        'synonyms': ['vigesimonoveno', 'vigésimo noveno', 'vigesimonovena', 'vigésima novena']
    },
    'trigésimo': {
        'id': 30,
        'synonyms': ['trigésima']
    },
    'último': {
        'id': -1,
        'synonyms': ['ultimo']
    },
}


if __name__ == '__main__':
    update_interaction()
