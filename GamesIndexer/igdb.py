import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os, csv, math, requests, json, argparse, re, urllib.request


# small struct to keep track of each game's data
class GameInfo:
    def __init__(self, game_id, name, order_name, year):
        self.id = game_id
        self.name = name
        self.order_name = order_name
        self.year = year
        self.img = None

    # generates TK image and returns it
    def get_img(self, w, h):
        if self.img is None:
            img_name = self.id + ".jpg"
            if os.path.exists(img_name):
                img = Image.open(img_name)
            else:
                img = Image.open("./default.jpg")
            # ratio_x, ratio_y = , (h - 55) / img.height
            ratio = w / img.width  # ratio_x if ratio_x < ratio_y else ratio_y
            self.img = ImageTk.PhotoImage(
                img.resize(
                    (math.floor(img.width * ratio), math.floor(img.height * ratio)),
                    Image.Resampling.LANCZOS,
                )
            )
        return self.img

    # order GameInfo by order_name
    def __lt__(self, other):
        return self.order_name < other.order_name


# A TK Frame that will group and show the actual game frames in a grid-like fashion
class GamesListPage(tk.Frame):
    def __init__(self, root, games_list, cols, game_width_px):
        tk.Frame.__init__(self, root)
        self.root = root
        self.cols = cols
        self.pack()

        # canvas with a scrollbar and a frame inside it
        self.canvas = tk.Canvas(
            self,
            width=root.winfo_screenwidth(),
            height=root.winfo_screenheight(),
            background="white",
        )
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left")

        # frame inside canvas has the actual game frames
        self.frame = tk.Frame(self.canvas, background="white")
        self.canvas.create_window(
            (0, 0), window=self.frame, anchor="nw", tags="self.frame"
        )
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.frame.bind("<Enter>", self._bound_to_mousewheel)
        self.frame.bind("<Leave>", self._unbound_to_mousewheel)

        # keep game frames in memory
        self.game_widgets = []
        self.make_game_frames(self.frame, games_list, game_width_px)

    # makes a game frame for each game in games_list, places it in proper grid position
    def make_game_frames(self, root, games_list, game_width_px):
        for index in range(len(games_list)):
            row = int(index / self.cols)
            col = index % self.cols
            game_frame = self.make_game_frame(root, games_list[index], game_width_px)
            game_frame.grid(row=row, column=col, sticky="s")
            self.game_widgets.append(game_frame)

    # makes a single game frame
    def make_game_frame(self, master_frame, game_info, game_width_px):
        frame = tk.Frame(master=master_frame, borderwidth=1, background="white")
        label_title = tk.Label(
            master=frame,
            text=game_info.name,
            background="white",
            wraplength=game_width_px,
            font="Helvetica 15 bold",
        )
        label_year = tk.Label(
            master=frame,
            text=str(game_info.year) + " - #" + game_info.id,
            background="white",
            wraplength=game_width_px,
        )
        label_img = tk.Label(
            master=frame,
            image=game_info.get_img(game_width_px, int(game_width_px * 1.9)),
        )
        label_pad = tk.Label(master=frame, background="white", font="Helvetica 5")
        label_title.pack()
        label_year.pack()
        label_img.pack()
        label_pad.pack()

        return frame

    def _on_frame_configure(self, _):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # when frame is focused, bind mousewheel
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    # when frame is unfocused, unbind mousewheel
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _on_mousewheel_linux_up(self, event):
        self.canvas.yview_scroll(-1, "units")


# loads .json, returns list of GameInfo
def build_games_list(json_name):
    games_list = []
    with open(json_name, newline="") as json_file:
        games_json = json.load(json_file)
        for game in games_json["games"]:
            games_list.append(
                GameInfo(game["id"], game["name"], game["order_name"], game["year"])
            )
    games_list.sort()
    return games_list


# loads .csv extracted from IGDB.com, queries IGDB.com for GameInfos, saves .json with same name
def process_csv(csv_name):
    games_json = []
    access_token = get_auth_token()

    with open(csv_name + ".csv", newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
        first_line_skipped = False
        for row in csv_reader:
            if not first_line_skipped:
                first_line_skipped = True
                continue
            game_json = call_api(row[0], access_token)
            games_json.append(game_json)

    with open(csv_name + ".json", "w") as outfile:
        json.dump({"games": games_json}, outfile, indent=4)


# taken from https://dev.twitch.tv/console/apps
CLIENT_ID = "<add it here>"
CLIENT_SECRET = "<add it here>"

# authenticates on Twitch with OAuth2
def get_auth_token():
    auth_url = (
        "https://id.twitch.tv/oauth2/token?client_id="
        + CLIENT_ID
        + "&client_secret="
        + CLIENT_SECRET
        + "&grant_type=client_credentials"
    )

    # make post to auth_url, get token
    response_decoded_json = requests.post(auth_url)
    response_json = response_decoded_json.json()
    access_token = response_json["access_token"]
    return access_token


# queries IGDB.com, returns json struct with game info
def call_api(game_id, access_token):
    # query game info
    game_api_url = "https://api.igdb.com/v4/games"
    header = {"Client-ID": CLIENT_ID, "Authorization": "Bearer " + access_token}
    response_decoded_json = requests.post(
        game_api_url,
        data="fields *,release_dates.*,cover.*; where id = " + str(game_id) + ";",
        headers=header,
    )
    response_json = response_decoded_json.json()[0]

    name = response_json["name"]

    # get earliest release year
    year = 0
    if "release_dates" in response_json:
        for release_year in response_json["release_dates"]:
            if "y" not in release_year:  # happens with TBD dates
                continue
            if release_year["y"] < year or year == 0:
                year = release_year["y"]
    if year == 0:
        print("\tEmpty year!")

    # get proper name to order game with
    order_name = name.lower().split(": ")[0].split(" - ")[0].split(", ")[0] + " "
    if order_name.startswith("the "):
        order_name = order_name[4:]
    order_name = re.sub(r"[^a-zA-Z0-9 ]", "", order_name)
    order_name = re.sub(r" [0-9]+ ", "", order_name)
    order_name = order_name.replace("  ", " ")
    order_name = order_name.replace(" i ", "").replace(" ii ", "").replace(" iii ", "")
    order_name = order_name.strip() + " " + str(year)

    # download cover img
    if "cover" in response_json:
        img_url = "https:" + response_json["cover"]["url"].replace(
            "/t_thumb/", "/t_cover_big/"
        )
        img_file_path = "./" + str(game_id) + ".jpg"
        if not os.path.exists(img_file_path):
            img_data = requests.get(img_url).content
            with open(img_file_path, "wb") as handler:
                handler.write(img_data)
    else:
        print("No image found!")

    game_json = {"id": game_id, "name": name, "order_name": order_name, "year": year}
    print(game_json)
    return game_json


# adds/removes games with args, or shows GUI otherwise
def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--list", default="", dest="list", help="""List.json to work on"""
    )
    parser.add_argument(
        "--add",
        default="",
        dest="add",
        help="""ID of game from IGDB.com to add on given --list""",
    )
    parser.add_argument(
        "--csv",
        default="",
        dest="csv",
        help="""IGDB.com CSV file name to process and convert to JSON""",
    )
    parser.add_argument(
        "--remove",
        default="",
        dest="remove",
        help="""ID of game from IGDB.com to remove on given --list""",
    )
    args = parser.parse_args()

    if len(args.add) != 0:
        if len(args.list) == 0:
            print("Please specify a target list to add game to!")
            exit(1)
        if os.path.exists(args.list + ".json"):
            with open(args.list + ".json", newline="") as json_file:
                games_json = json.load(json_file)
        else:
            games_json = {"games": []}
        access_token = get_auth_token()
        game_json = call_api(args.add, access_token)
        games_json["games"] = [
            game for game in games_json["games"] if game["id"] != args.add
        ]
        games_json["games"].append(game_json)
        with open(args.list + ".json", "w") as outfile:
            json.dump(games_json, outfile, indent=4)
        exit(0)

    if len(args.remove) != 0:
        if len(args.list) == 0:
            print("Please specify a target list to remove game from!")
            exit(1)
        with open(args.list + ".json", newline="") as json_file:
            games_json = json.load(json_file)
        games_json["games"] = [
            game for game in games_json["games"] if game["id"] != args.remove
        ]
        with open(args.list + ".json", "w") as outfile:
            json.dump(games_json, outfile, indent=4)
        exit(0)

    if len(args.csv) != 0:
        process_csv("./" + args.csv)

    window = tk.Tk()
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    window.title("Games Indexer")
    window.iconphoto(False, tk.PhotoImage(file="./igdb.png"))
    window.update()

    cols = 5
    game_width_px = (window.winfo_width() - 40) / 5

    tab_control = tk.ttk.Notebook(window)
    tab_control.pack(expand=1, fill="both")

    list_of_jsons = []
    for file in os.listdir("."):
        if not file.endswith(".json"):
            continue
        list_of_jsons.append(file)

    list_of_games_lists = []
    list_of_jsons.sort()
    for file in list_of_jsons:
        print(file)

        games_list = build_games_list(os.path.join(".", file))
        list_of_games_lists.append(
            games_list
        )  # append to list so images don't get garbage collected
        tab = tk.ttk.Frame(tab_control)
        tab_control.add(tab, text=file[:-5])
        tab.update()
        GamesListPage(tab, games_list, cols, game_width_px)

    window.mainloop()


if __name__ == "__main__":
    main()
