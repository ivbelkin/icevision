import argparse
import pandas as pd

def build_parser():
    parser = argparse.ArgumentParser("Add polygons according to sign class")
    parser.add_argument(
        "--input-file",
        type=str
    )
    parser.add_argument(
        "--output-file",
        type=str
    )
    return parser


labels_with_data = {'8.2.1', '3.4', '6.10.2', '8.11', '8.2.6', '3.25', '5.32', '8.2.5', '8.4.1', \
                    '6.9.2', '8.1.4', '8.1.1', '8', '5.31', '8.5.4', '3.13', '6.13', '7.5', '8.2.2', \
                    '3.11', '6.9.1', '5.23.1', '1.13', '6.10.1', '6.11', '5.24.1', '3.24'}

most_common = {'8.2.1': '400 м', '5.23.1': 'Заречье', '3.24': '20', '1.13': '6 %', '7.5': '200 м', \
               '6.10.1': 'усадьба “Назарьево” “Nazarevo” estate', '8.1.1': '250 м', '3.13': '4,5 м',\
               '6.9.2': 'М9 Псков М3 Калуга МКАД', '6.10.2': '53', '8.2.2': '70 м', '8.1.4': '50 м', \
               '3.4': '3,5 т', '3.25': '80', '5.24.1': 'Ново-Ивановское', '6.13': '37 мосавтодор', \
               '8.4.1': '12 т без пропуска', '8.5.4': '6.00 - 22.00', '8': 'Пропан', \
               '6.9.1': 'МКАД Сколковское ш. 0.6 Ленинский пр-т 8.3', '8.2.5': '600 м', \
               '5.31': '20', '5.32': '40', '6.11': 'р. Сетунь', '8.11': '12 т', '3.11': '5 т', '8.2.6': '50 м'}


def get_data(label):
    label = str(label)
    if label in labels_with_data:
        return most_common[label]
    else:
        return ""


def main(args):
    df = pd.read_csv(args.input_file, sep='\t', dtype=str)
    df['data'] = df['class'].apply(get_data)
    df.to_csv(args.output_file, sep='\t', index=False)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
