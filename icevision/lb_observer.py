import requests
from bs4 import BeautifulSoup
from time import sleep
import argparse
import os
import json
import random

URL = "https://visiontest.misis.ru/"

TABLE_HEADER = [
    "place", "team", "time", "2.1", "2.4", "3.1", "3.24", "3.27", "4.1", "4.2", "5.19", "5.20", "8.22", "all"
]


def build_parser():
    parser = argparse.ArgumentParser("Fetch and store leader board from https://visiontest.misis.ru/")
    parser.add_argument(
        "--log-file",
        type=str,
        help="file, where logs will be saved"
    )
    parser.add_argument(
        "--interval",
        type=str,
        help="time interval in seconds between requests"
    )
    parser.add_argument(
        "--show-best",
        action="store_true",
        help="only show best results for each command and exit"
    )
    return parser


def fetch():
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    tbody = soup.find("tbody")
    result = {}
    for tr in tbody.find_all("tr"):
        team_name = None
        team_result = {"results": {}}
        for name, td in zip(TABLE_HEADER, tr.find_all("td")):
            if name == "team":
                team_name = td.get_text()
            elif name == "time":
                team_result["time"] = td.get_text()
            else:
                divs = td.find_all("div")
                if len(divs) == 2:
                    team_result["results"][name] = {}
                    team_result["results"][name]["total"] = float(divs[0].get_text().replace("−", "-"))

                    spans = divs[1].find_all("span")

                    team_result["results"][name]["score"] = float(spans[0].get_text().replace("−", "-"))
                    team_result["results"][name]["penalty"] = float(spans[1].get_text().replace("−", "-"))
                else:
                    team_result["results"][name] = None

        result[team_name] = team_result
    return result


def main(args):
    if os.path.exists(args.log_file):
        with open(args.log_file, "r") as f:
            results = json.load(f)
    else:
        results = {}

    if args.show_best:
        if len(results) == 0:
            print("Nothing to show")
        else:
            for team_name, team_results in results.items():
                team_result_best = team_results[0]
                for team_result in team_results:
                    if team_result_best["results"]["all"] is None:
                        team_result_best = team_result
                    elif team_result["results"]["all"] is not None:
                        if team_result["results"]["all"]["total"] > team_result_best["results"]["all"]["total"]:
                            team_result_best = team_result
                if team_result_best["results"]["all"] is not None:
                    print(team_name, team_result_best["results"]["all"]["total"])
    else:
        i = 1
        interval = list(map(int, args.interval.split(",")))
        while True:
            try:
                print("Request", i)
                result = fetch()
                for team_name, team_result in result.items():
                    if team_name not in results:
                        results[team_name] = [team_result]
                    elif team_result["time"] != results[team_name][-1]["time"]:
                        results[team_name].append(team_result)
                with open(args.log_file, "w") as f:
                    json.dump(results, f)
                t = random.randint(*interval)
                print("Sleep", t, "seconds")
                sleep(t)
                i += 1
            except KeyboardInterrupt:
                print("Stop")
            except:
                print("Error")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
