import os
import json
import random
import argparse
from datetime import datetime
from tqdm import tqdm
from .agent import Agent

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
    def __init__(self, model_name: str='gpt-3.5-turbo', temperature: float=0, num_players: int=3, save_file_dir: str=None, openai_api_key: str=None, prompts_path: str=None, max_round: int=3, sleep_time: float=0) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.save_file_dir = save_file_dir
        self.openai_api_key = openai_api_key
        self.max_round = max_round
        self.sleep_time = sleep_time

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        self.save_file = {
            'start_time': current_time,
            'end_time': '',
            'model_name': model_name,
            'temperature': temperature,
            'num_players': num_players,
            'success': False,
            'source': '',
            'base_answer': '',
            'debate_answer': '',
            'Reason': '',
            'Supported Side': '',
            'players': {},
        }
        prompts = json.load(open(prompts_path))
        self.save_file.update(prompts)
        self.init_prompt()

        if self.save_file['base_answer'] == "":
            self.create_base()

        self.creat_agents()
        self.init_agents()

    def init_prompt(self):
        def prompt_replace(key):
            self.save_file[key] = self.save_file[key].replace("##source##", self.save_file["source"])
        prompt_replace("base_prompt")
        prompt_replace("player_meta_prompt")
        prompt_replace("moderator_meta_prompt")
        prompt_replace("judge_prompt_last2")

    def create_base(self):
        print(f"\n===== Fake News Detection Task =====\n{self.save_file['base_prompt']}\n")
        agent = CourtRoomDebatePlayer(model_name=self.model_name, name='Baseline', temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time)
        agent.add_event(self.save_file['base_prompt'])
        base_answer = agent.ask()
        agent.add_memory(base_answer)
        self.save_file['base_answer'] = base_answer
        self.save_file['affirmative_prompt'] = self.save_file['affirmative_prompt'].replace("##base_answer##", base_answer)
        self.save_file['players'][agent.name] = agent.memory_lst

    def creat_agents(self):
        self.players = [
            CourtRoomDebatePlayer(model_name=self.model_name, name=name, temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time) for name in NAME_LIST
        ]
        self.prosecution = self.players[0]
        self.defense = self.players[1]
        self.judge = self.players[2]

    def init_agents(self):
        self.prosecution.set_meta_prompt(self.save_file['player_meta_prompt'])
        self.defense.set_meta_prompt(self.save_file['player_meta_prompt'])
        self.judge.set_meta_prompt(self.save_file['moderator_meta_prompt'])

        print(f"===== Debate Round-1 =====\n")
        self.prosecution.add_event(self.save_file['affirmative_prompt'])
        self.pros_ans = self.prosecution.ask()
        self.prosecution.add_memory(self.pros_ans)

        self.defense.add_event(self.save_file['negative_prompt'].replace('##aff_ans##', self.pros_ans))
        self.def_ans = self.defense.ask()
        self.defense.add_memory(self.def_ans)

        self.judge.add_event(self.save_file['moderator_prompt'].replace('##aff_ans##', self.pros_ans).replace('##neg_ans##', self.def_ans).replace('##round##', 'first'))
        self.jud_ans = self.judge.ask()
        self.judge.add_memory(self.jud_ans)
        self.jud_ans = eval(self.jud_ans)

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
        }
        return dct[num]

    def save_file_to_json(self, id):
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        save_file_path = os.path.join(self.save_file_dir, f"{id}.json")

        self.save_file['end_time'] = current_time
        json_str = json.dumps(self.save_file, ensure_ascii=False, indent=4)
        with open(save_file_path, 'w') as f:
            f.write(json_str)

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
                self.prosecution.add_event(self.save_file['debate_prompt'].replace('##oppo_ans##', self.def_ans))
                self.pros_ans = self.prosecution.ask()
                self.prosecution.add_memory(self.pros_ans)

                self.defense.add_event(self.save_file['debate_prompt'].replace('##oppo_ans##', self.pros_ans))
                self.def_ans = self.defense.ask()
                self.defense.add_memory(self.def_ans)

                self.judge.add_event(self.save_file['moderator_prompt'].replace('##aff_ans##', self.pros_ans).replace('##neg_ans##', self.def_ans).replace('##round##', self.round_dct(round+2)))
                self.jud_ans = self.judge.ask()
                self.judge.add_memory(self.jud_ans)
                self.jud_ans = eval(self.jud_ans)

        if self.jud_ans["debate_answer"] != '':
            self.save_file.update(self.jud_ans)
            self.save_file['success'] = True

        else:
            judge_player = CourtRoomDebatePlayer(model_name=self.model_name, name='Judge', temperature=self.temperature, openai_api_key=self.openai_api_key, sleep_time=self.sleep_time)
            pros_ans = self.prosecution.memory_lst[2]['content']
            def_ans = self.defense.memory_lst[2]['content']

            judge_player.set_meta_prompt(self.save_file['moderator_meta_prompt'])

            judge_player.add_event(self.save_file['judge_prompt_last1'].replace('##aff_ans##', pros_ans).replace('##neg_ans##', def_ans))
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            judge_player.add_event(self.save_file['judge_prompt_last2'])
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            ans = eval(ans)
            if ans["debate_answer"] != '':
                self.save_file['success'] = True
            self.save_file.update(ans)
            self.players.append(judge_player)

        for player in self.players:
            self.save_file['players'][player.name] = player.memory_lst

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input-file", type=str, required=True, help="Input file path")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="Output file dir")
    parser.add_argument("-k", "--api-key", type=str, required=True, help="OpenAI api key")
    parser.add_argument("-m", "--model-name", type=str, default="gpt-3.5-turbo", help="Model name")
    parser.add_argument("-t", "--temperature", type=float, default=0, help="Sampling temperature")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    openai_api_key = args.api_key

    current_script_path = os.path.abspath(__file__)
    FND_path = current_script_path.rsplit("/", 2)[0]

    config = json.load(open(f"{FND_path}/code/utils/config4fnd.json", "r"))

    inputs = open(args.input_file, "r").readlines()
    inputs = [l.strip() for l in inputs]

    save_file_dir = args.output_dir
    if not os.path.exists(save_file_dir):
        os.mkdir(save_file_dir)

    for id, input in enumerate(tqdm(inputs)):
        prompts_path = f"{save_file_dir}/{id}-config.json"

        config['source'] = input
        with open(prompts_path, 'w') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

        debate = Debate(save_file_dir=save_file_dir, num_players=3, openai_api_key=openai_api_key, prompts_path=prompts_path, temperature=0, sleep_time=0)
        debate.run()
        debate.save_file_to_json(id)