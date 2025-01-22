import os
import json
import random
from .agent import Agent

openai_api_key = "Your-OpenAI-Api-Key"

NAME_LIST = [
    "Prosecution",
    "Defense",
    "Judge"
]

class CourtRoomDebatePlayer(Agent):
    def __init__(self, model_name: str, name: str, temperature: float, openai_api_key: str, sleep_time: float) -> None:
        super(CourtRoomDebatePlayer, self).__init__(model_name, name, temperature, sleep_time)
        self.openai_api_key = openai_api_key

class Debate:
    def __init__(self, model_name: str='gpt-3.5-turbo', temperature: float=0, num_players: int=3, openai_api_key: str=None, config: dict=None, max_round: int=3, sleep_time: float=0) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.openai_api_key = openai_api_key
        self.config = config
        self.max_round = max_round
        self.sleep_time = sleep_time

        self.init_prompt()
        self.creat_agents()
        self.init_agents()

    def init_prompt(self):
        def prompt_replace(key):
            self.config[key] = self.config[key].replace("##debate_topic##", self.config["debate_topic"])
        prompt_replace("player_meta_prompt")
        prompt_replace("moderator_meta_prompt")
        prompt_replace("affirmative_prompt")
        prompt_replace("judge_prompt_last2")

    def creat_agents(self):
        self.players = [
            CourtRoomDebatePlayer(model_name=self.model_name, name=name, temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time) for name in NAME_LIST
        ]
        self.prosecution = self.players[0]
        self.defense = self.players[1]
        self.judge = self.players[2]

    def init_agents(self):
        self.prosecution.set_meta_prompt(self.config['player_meta_prompt'])
        self.defense.set_meta_prompt(self.config['player_meta_prompt'])
        self.judge.set_meta_prompt(self.config['moderator_meta_prompt'])

        print(f"===== Debate Round-1 =====\n")
        self.prosecution.add_event(self.config['affirmative_prompt'])
        self.pros_ans = self.prosecution.ask()
        self.prosecution.add_memory(self.pros_ans)
        self.config['base_answer'] = self.pros_ans

        self.defense.add_event(self.config['negative_prompt'].replace('##aff_ans##', self.pros_ans))
        self.def_ans = self.defense.ask()
        self.defense.add_memory(self.def_ans)

        self.judge.add_event(self.config['moderator_prompt'].replace('##aff_ans##', self.pros_ans).replace('##neg_ans##', self.def_ans).replace('##round##', 'first'))
        self.jud_ans = self.judge.ask()
        self.judge.add_memory(self.jud_ans)
        self.jud_ans = eval(self.jud_ans)

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
        }
        return dct[num]

    def print_answer(self):
        print("\n\n===== Debate Done! =====")
        print("\n----- Debate Topic -----")
        print(self.config["debate_topic"])
        print("\n----- Base Answer -----")
        print(self.config["base_answer"])
        print("\n----- Debate Answer -----")
        print(self.config["debate_answer"])
        print("\n----- Debate Reason -----")
        print(self.config["Reason"])

    def broadcast(self, msg: str):
        for player in self.players:
            player.add_event(msg)

    def speak(self, speaker: str, msg: str):
        if not msg.startswith(f"{speaker}: "):
            msg = f"{speaker}: {msg}"
        for player in self.players:
            if player.name != speaker:
                player.add_event(msg)

    def ask_and_speak(self, player: CourtRoomDebatePlayer):
        ans = player.ask()
        player.add_memory(ans)
        self.speak(player.name, ans)

    def run(self):
        for round in range(self.max_round - 1):
            if self.jud_ans["debate_answer"] != '':
                break
            else:
                print(f"===== Debate Round-{round+2} =====\n")
                self.prosecution.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.def_ans))
                self.pros_ans = self.prosecution.ask()
                self.prosecution.add_memory(self.pros_ans)

                self.defense.add_event(self.config['debate_prompt'].replace('##oppo_ans##', self.pros_ans))
                self.def_ans = self.defense.ask()
                self.defense.add_memory(self.def_ans)

                self.judge.add_event(self.config['moderator_prompt'].replace('##aff_ans##', self.pros_ans).replace('##neg_ans##', self.def_ans).replace('##round##', self.round_dct(round+2)))
                self.jud_ans = self.judge.ask()
                self.judge.add_memory(self.jud_ans)
                self.jud_ans = eval(self.jud_ans)

        if self.jud_ans["debate_answer"] != '':
            self.config.update(self.jud_ans)
            self.config['success'] = True

        else:
            judge_player = CourtRoomDebatePlayer(model_name=self.model_name, name='Judge', temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time)
            pros_ans = self.prosecution.memory_lst[2]['content']
            def_ans = self.defense.memory_lst[2]['content']

            judge_player.set_meta_prompt(self.config['moderator_meta_prompt'])

            judge_player.add_event(self.config['judge_prompt_last1'].replace('##aff_ans##', pros_ans).replace('##neg_ans##', def_ans))
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            judge_player.add_event(self.config['judge_prompt_last2'])
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            ans = eval(ans)
            if ans["debate_answer"] != '':
                self.config['success'] = True
            self.config.update(ans)
            self.players.append(judge_player)

        self.print_answer()

if __name__ == "__main__":
    current_script_path = os.path.abspath(__file__)
    FND_path = current_script_path.rsplit("/", 1)[0]

    while True:
        debate_topic = ""
        while debate_topic == "":
            debate_topic = input(f"\nEnter your debate topic: ")

        config = json.load(open(f"{FND_path}/code/utils/config4fnd.json", "r"))
        config['debate_topic'] = debate_topic

        debate = Debate(num_players=3, openai_api_key=openai_api_key, config=config, temperature=0, sleep_time=0)
        debate.run()